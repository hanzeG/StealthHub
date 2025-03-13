// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;

contract RightMerkleTree {
    address public poseidon2Contract;
    bytes32 public initRoot;
    bytes32 public currentRoot;
    uint256 public currentIndex;
    uint256 public nextIndex;
    bool public nextIsEven;

    // Maximum tree depth.
    uint256 public constant MAX_DEPTH = 32;

    // The insert stack is stored as a fixed-size array.
    bytes32[MAX_DEPTH] public insertStack;
    uint256 public insertStackLength;

    constructor(bytes32 _initRoot, address _poseidon2Contract) {
        poseidon2Contract = _poseidon2Contract;
        initRoot = _initRoot;
        currentRoot = _initRoot;
        currentIndex = 1;
        nextIndex = currentIndex + 1;
        nextIsEven = (nextIndex % 2 == 0);

        insertStack[0] = _initRoot;
        insertStackLength = 1;
    }

    /// @notice Inserts a new commitment and updates the tree.
    /// @param commitment The new commitment.
    /// @return The updated current index and current root.
    function insert(bytes32 commitment) public returns (uint256, bytes32) {
        uint256 countHash = _countOnes(currentIndex);
        require(insertStackLength == countHash, "insertStack length mismatch");

        // Compute the new root using a memory array.
        bytes32[MAX_DEPTH + 1] memory rightPreimage;
        rightPreimage[0] = commitment;
        for (uint256 i = 0; i < countHash; i++) {
            rightPreimage[i + 1] = _callPoseidon2Yul3(
                insertStack[i],
                rightPreimage[i]
            );
        }
        bytes32 newRoot = rightPreimage[countHash];

        // Update indices.
        currentIndex += 1;
        nextIndex = currentIndex + 1;
        nextIsEven = (nextIndex % 2 == 0);

        // Use a temporary memory array for updating the insertStack.
        bytes32[MAX_DEPTH] memory tempStack;
        uint256 tempLength = insertStackLength;
        for (uint256 i = 0; i < tempLength; i++) {
            tempStack[i] = insertStack[i];
        }

        if (nextIsEven) {
            require(tempLength < MAX_DEPTH, "insertStack overflow");
            // Shift elements to the right.
            for (uint256 i = tempLength; i > 0; i--) {
                tempStack[i] = tempStack[i - 1];
            }
            tempStack[0] = commitment;
            tempLength += 1;
        } else {
            uint256 lsBit = currentIndex & ((~currentIndex) + 1);
            uint256 indexVal = _getLeastSignificantBitIndex(lsBit);
            require(indexVal <= tempLength, "Slice index out of bounds");
            // Remove the first 'indexVal' elements.
            for (uint256 i = 0; i < tempLength - indexVal; i++) {
                tempStack[i] = tempStack[i + indexVal];
            }
            tempLength = tempLength - indexVal;
            require(tempLength < MAX_DEPTH, "insertStack overflow");
            // Shift elements right and insert the new value.
            for (uint256 i = tempLength; i > 0; i--) {
                tempStack[i] = tempStack[i - 1];
            }
            tempStack[0] = rightPreimage[indexVal];
            tempLength += 1;
        }

        // Write back the updated stack to storage.
        for (uint256 i = 0; i < tempLength; i++) {
            insertStack[i] = tempStack[i];
        }
        insertStackLength = tempLength;
        currentRoot = newRoot;
        return (currentIndex, currentRoot);
    }

    /// @notice Calls the Poseidon2 hash function.
    /// @param input1 The first input.
    /// @param input2 The second input.
    /// @return The hash result.
    function _callPoseidon2Yul3(
        bytes32 input1,
        bytes32 input2
    ) public returns (bytes32) {
        (bool success, bytes memory result) = poseidon2Contract.call(
            abi.encode(input1, input2)
        );
        require(success, "Poseidon2 call failed");
        return bytes32(result);
    }

    /// @notice Counts the number of one bits in the binary representation of x.
    /// @param x The input number.
    /// @return count The number of ones.
    function _countOnes(uint256 x) internal pure returns (uint256 count) {
        while (x != 0) {
            if ((x & 1) == 1) {
                count++;
            }
            x = x >> 1;
        }
    }

    /// @notice Gets the index (log2) of a power-of-two number.
    /// @param x The power-of-two number.
    /// @return index The zero-based index.
    function _getLeastSignificantBitIndex(
        uint256 x
    ) internal pure returns (uint256 index) {
        while (x > 1) {
            x = x >> 1;
            index++;
        }
    }
}
