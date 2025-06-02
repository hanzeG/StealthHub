// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;

import "./MmrWithHistory.sol";
import "./ReentrancyGuard.sol";

interface IVerifier {
    function verifyProof(
        uint[2] calldata _pA,
        uint[2][2] calldata _pB,
        uint[2] calldata _pC,
        uint[1] calldata _pubSignals
    ) external returns (bool);
}

abstract contract Sha is MmrWithHistory, ReentrancyGuard {
    uint256 private m;

    IVerifier public immutable verifier1;
    IVerifier public immutable verifier2;

    mapping(bytes32 => bool) public nullifierHashes;
    // We store all commitments just to prevent accidental deposits with the same commitment
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
        // bytes32 indexed commitment2,
        uint32 leafIndex1,
        // uint32 leafIndex2,
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
    @param _verifier1 Shielded transfer verifier
    @param _verifier2 Withdraw verifier
    @param _poseidon2Contract The address of the Poseidon2 hash contract
    @param _initRoot The init root of the Merkle Tree
    */
    constructor(
        IVerifier _verifier1,
        IVerifier _verifier2,
        address _poseidon2Contract,
        bytes32 _initRoot
    ) MmrWithHistory(_initRoot, _poseidon2Contract) {
        verifier1 = _verifier1;
        verifier2 = _verifier2;
    }

    /**
    @dev Deposit funds into the contract. The caller must send (for ETH) or approve (for ERC20) a value equal to or `denomination` of this instance.
    @param _commitment The note commitment, which is Poseidon Hash (nullifier + secret)
    @param proof The zkSNARK proof data, which is an array of circuit public inputs and is required for sh-a.
    */
    function deposit(
        bytes32 _commitment,
        Proof calldata proof,
        uint256 asset
    ) external payable nonReentrant {
        require(
            verifier1.verifyProof(
                proof.pA,
                proof.pB,
                proof.pC,
                proof.pubSignals
            ),
            "Invalid deposit proof"
        );

        // require(!commitments[_commitment], "The commitment has been submitted");
        (uint32 insertedIndex, bytes32 currentRoot) = _insert(_commitment);
        commitments[_commitment] = true;
        _processDeposit(asset);

        emit Deposit(_commitment, insertedIndex, block.timestamp);
    }

    /** @dev This function is defined in a child contract */
    function _processDeposit(uint256 asset) internal virtual;

    function shieldedTransfer(
        bytes32 _commitment1,
        // bytes32 _commitment2,
        Proof calldata proof,
        uint256 asset
    ) external payable nonReentrant {
        require(
            verifier1.verifyProof(
                proof.pA,
                proof.pB,
                proof.pC,
                proof.pubSignals
            ),
            "Invalid deposit proof"
        );

        // only one commitment is required for shielded transfer in sha-a

        // require(!commitments[_commitment1], "The commitment has been submitted");
        // require(
        //     !commitments[_commitment2],
        //     "The commitment has been submitted"
        // );
        (uint32 insertedIndex1, bytes32 currentRoot1) = _insert(_commitment1);
        // (uint32 insertedIndex2, bytes32 currentRoot2) = _insert(_commitment2);
        commitments[_commitment1] = true;
        // commitments[_commitment2] = true;

        emit ShieldedTransfer(
            _commitment1,
            // _commitment2,
            insertedIndex1,
            // insertedIndex2,
            block.timestamp
        );
    }

    function _processShieldedTransfer(uint256 asset) internal virtual;

    /**
    @dev Withdraw a deposit from the contract. `proof` is zkSNARK proof data, and input is an array of circuit public inputs.
    `input` array consists of:
      - Merkle root of all deposits in the contract
      - Hash of unique deposit nullifier to prevent double spends
      - The recipient of funds
      - Optional fee that goes to the transaction sender (usually a relay)
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
            "The note has already been spent"
        );
        // require(isKnownRoot(root), "Cannot find your Merkle root"); // Make sure to use a recent one
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

    /** @dev This function is defined in a child contract */
    function _processWithdraw(
        address payable _recipient,
        address payable _relayer,
        uint256 _fee,
        uint256 _refund,
        uint256 asset
    ) internal virtual;

    /** @dev Whether a note is already spent */
    function isSpent(bytes32 _nullifierHash) public view returns (bool) {
        return nullifierHashes[_nullifierHash];
    }

    /** @dev Whether an array of notes is already spent */
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
     * @dev Set the amount `m`.
     * @param _m The amount to be set.
     */
    function setAmount(uint256 _m) external {
        m = _m;
    }

    /**
     * @dev Get the currently stored amount `m`.
     * @return The current stored amount.
     */
    function getAmount() external view returns (uint256) {
        return m;
    }

    /**
     * @dev Get the `msg.value` of the current call.
     * @return The `msg.value` of the current call.
     */
    function getMsgValue() external payable returns (uint256) {
        return msg.value;
    }

    /**
     * @dev Check whether the stored amount `m` is equal to `msg.value`.
     * @return True if they are equal, otherwise false.
     */
    function isAmountEqualToMsgValue() external payable returns (bool) {
        return m == msg.value;
    }
}
