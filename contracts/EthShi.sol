// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;

import "./Shi.sol";

contract EthShi is Shi {
    constructor(
        // IVerifier _verifier1,
        IVerifier _verifier2,
        IVerifier _verifier3,
        address _poseidon2Contract,
        uint32 _merkleTreeHeight
    ) Shi(_verifier2, _verifier3, _poseidon2Contract, _merkleTreeHeight) {}

    function _processDeposit(uint256 _asset) internal override {
        require(
            msg.value == _asset,
            "Please send correct amount of asset along with transaction"
        );
    }

    function _processWithdraw(
        address payable _recipient,
        address payable _relayer,
        uint256 _fee,
        uint256 _refund,
        uint256 _asset
    ) internal override {
        // sanity checks
        require(
            msg.value == 0,
            "Message value is supposed to be zero for ETH instance"
        );
        require(
            _refund == 0,
            "Refund value is supposed to be zero for ETH instance"
        );

        (bool success, ) = _recipient.call{value: _asset - _fee}("");
        require(success, "payment to _recipient did not go thru");
        if (_fee > 0) {
            (success, ) = _relayer.call{value: _fee}("");
            require(success, "payment to _relayer did not go thru");
        }
    }
}
