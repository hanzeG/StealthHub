// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;

import "./MerkleTreeWithHistory.sol";
import "./ReentrancyGuard.sol";

interface IVerifier {
    function verifyProof(
        uint[2] calldata _pA,
        uint[2][2] calldata _pB,
        uint[2] calldata _pC,
        uint[1] calldata _pubSignals
    ) external returns (bool);
}

abstract contract IMCSH is MerkleTreeWithHistory, ReentrancyGuard {
    uint256 private m;

    // IVerifier public immutable verifier1;
    IVerifier public immutable verifier2;
    IVerifier public immutable verifier3;

    mapping(bytes32 => bool) public nullifierHashes;
    // we store all commitments just to prevent accidental deposits with the same commitment
    mapping(bytes32 => bool) public commitments;

    event Deposit(
        bytes32 indexed commitment,
        uint32 leafIndex,
        uint256 timestamp
    );
    event Withdrawal(
        address to,
        bytes32 nullifierHash,
        address indexed relayer,
        uint256 fee
    );
    event ShieldedTransfer(
        bytes32 indexed commitment1,
        bytes32 indexed commitment2,
        uint32 leafIndex1,
        uint32 leafIndex2,
        uint256 timestamp
    );

    struct Proof {
        uint[2] pA;
        uint[2][2] pB;
        uint[2] pC;
        uint[1] pubSignals;
    }

    /**
    @dev The constructor

    @param _verifier2 shielded transfer verifier
    @param _verifier3 withdraw verifier
    @param _poseidon2Contract the address of poseidon2 hash contract
    @param _merkleTreeHeight the height of deposits' Merkle Tree
  */
    constructor(
        // IVerifier _verifier1,
        IVerifier _verifier2,
        IVerifier _verifier3,
        address _poseidon2Contract,
        uint32 _merkleTreeHeight
    ) MerkleTreeWithHistory(_merkleTreeHeight, _poseidon2Contract) {
        // verifier1 = _verifier1;
        verifier2 = _verifier2;
        verifier3 = _verifier3;
    }

    /**
    @dev Deposit funds into the contract. The caller must send (for ETH) or approve (for ERC20) value equal to or `denomination` of this instance.
    @param _commitment the note commitment, which is PedersenHash(nullifier + secret)
  */
    function deposit(
        bytes32 _commitment,
        // Proof calldata proof,
        uint256 asset
    ) external payable nonReentrant {
        // require(
        //     verifier1.verifyProof(
        //         proof.pA,
        //         proof.pB,
        //         proof.pC,
        //         proof.pubSignals
        //     ),
        //     "Invalid deposit proof"
        // );
        // require(!commitments[_commitment], "The commitment has been submitted");
        uint32 insertedIndex = _insert(_commitment);
        commitments[_commitment] = true;
        _processDeposit(asset);

        emit Deposit(_commitment, insertedIndex, block.timestamp);
    }

    /** @dev this function is defined in a child contract */
    function _processDeposit(uint256 asset) internal virtual;

    function shieldedTransfer(
        bytes32 _commitment1,
        bytes32 _commitment2,
        Proof calldata proof,
        uint256 asset
    ) external payable nonReentrant {
        require(
            verifier3.verifyProof(
                proof.pA,
                proof.pB,
                proof.pC,
                proof.pubSignals
            ),
            "Invalid deposit proof"
        );
        // require(!commitments[_commitment1], "The commitment has been submitted");
        // require(
        //     !commitments[_commitment2],
        //     "The commitment has been submitted"
        // );
        uint32 insertedIndex1 = _insert(_commitment1);
        uint32 insertedIndex2 = _insert(_commitment2);
        commitments[_commitment1] = true;
        commitments[_commitment2] = true;

        emit ShieldedTransfer(
            _commitment1,
            _commitment2,
            insertedIndex1,
            insertedIndex2,
            block.timestamp
        );
    }

    /**
    @dev Withdraw a deposit from the contract. `proof` is a zkSNARK proof data, and input is an array of circuit public inputs
    `input` array consists of:
      - merkle root of all deposits in the contract
      - hash of unique deposit nullifier to prevent double spends
      - the recipient of funds
      - optional fee that goes to the transaction sender (usually a relay)
  */
    function withdraw(
        Proof calldata proof,
        bytes32 root,
        bytes32 nullifierHash,
        address payable recipient,
        address payable relayer,
        uint256 fee,
        uint256 refund,
        uint256 asset
    ) external payable nonReentrant {
        require(
            !nullifierHashes[nullifierHash],
            "The note has been already spent"
        );
        require(isKnownRoot(root), "Cannot find your merkle root"); // Make sure to use a recent one
        require(
            verifier2.verifyProof(
                proof.pA,
                proof.pB,
                proof.pC,
                proof.pubSignals
            ),
            "Invalid withdraw proof"
        );

        nullifierHashes[nullifierHash] = true;
        _processWithdraw(recipient, relayer, fee, refund, asset);
        emit Withdrawal(recipient, nullifierHash, relayer, fee);
    }

    /** @dev this function is defined in a child contract */
    function _processWithdraw(
        address payable _recipient,
        address payable _relayer,
        uint256 _fee,
        uint256 _refund,
        uint256 asset
    ) internal virtual;

    /** @dev whether a note is already spent */
    function isSpent(bytes32 _nullifierHash) public view returns (bool) {
        return nullifierHashes[_nullifierHash];
    }

    /** @dev whether an array of notes is already spent */
    function isSpentArray(
        bytes32[] calldata _nullifierHashes
    ) external view returns (bool[] memory spent) {
        spent = new bool[](_nullifierHashes.length);
        for (uint256 i = 0; i < _nullifierHashes.length; i++) {
            if (isSpent(_nullifierHashes[i])) {
                spent[i] = true;
            }
        }
    }

    /**
     * @dev 设置金额 m。
     * @param _m 要设置的金额值。
     */
    function setAmount(uint256 _m) external {
        m = _m;
    }

    /**
     * @dev 获取当前存储的金额 m。
     * @return 当前存储的金额值。
     */
    function getAmount() external view returns (uint256) {
        return m;
    }

    /**
     * @dev 获取当前调用时的 msg.value。
     * @return 当前调用时的 msg.value 值。
     */
    function getMsgValue() external payable returns (uint256) {
        return msg.value;
    }

    /**
     * @dev 检查存储的金额 m 是否等于 msg.value。
     * @return 如果相等返回 true，否则返回 false。
     */
    function isAmountEqualToMsgValue() external payable returns (bool) {
        return m == msg.value;
    }
}
