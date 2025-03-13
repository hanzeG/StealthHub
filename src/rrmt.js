const { poseidon2Hash } = require("./utils");
const assert = require("assert");

// Right Merkle Tree (rMT) class with Poseidon2 hash
class RightMerkleTree {
    constructor() {
        this.currentRoot = null;
        this.currentIndex = 0;
        this.nextIndex = this.currentIndex + 1;
        this.nextIsEven = this.nextIndex % 2 === 0;
        this.insertStack = [null];

        console.log("Constructor initialized:");
        console.log("currentRoot:", this.currentRoot);
        console.log("currentIndex:", this.currentIndex);
        console.log("nextIndex:", this.nextIndex);
        console.log("nextIsEven:", this.nextIsEven);
        console.log("insertStack:", this.insertStack);
    }

    async insert(commitment) {
        console.log("\nInserting commitment:", commitment);

        let countHash = this.currentIndex.toString(2).split("0").join("").length;
        console.log("countHash:", countHash);
        console.log("insertStack (before assert):", this.insertStack);
        assert(this.insertStack.length === countHash, "insertStack length is not equal to countHash");

        // Calculate the new root
        let tmp = new Array(3).fill(0);
        let rightPreimage = new Array(countHash + 1).fill(0);
        rightPreimage[0] = commitment;
        console.log("rightPreimage (initial):", rightPreimage);

        for (let i = 0; i < countHash; i++) {
            tmp = await poseidon2Hash([this.insertStack[i], rightPreimage[i], 1]);
            rightPreimage[i + 1] = tmp[0];
        }

        this.currentRoot = rightPreimage.at(-1);
        console.log("Updated currentRoot:", this.currentRoot);

        this.currentIndex += 1;

        // Update nextIndex and related variables
        this.nextIndex = this.currentIndex + 1;
        this.nextIsEven = this.nextIndex % 2 === 0;

        // Update insertStack
        if (this.nextIsEven) {
            console.log("nextIndex is even, inserting commitment at the beginning of insertStack");
            this.insertStack.unshift(commitment);
        } else {
            let index = Math.log2(this.currentIndex & -this.currentIndex) | 0;
            console.log("Index for slice:", index);
            this.insertStack = this.insertStack.slice(index);
            this.insertStack.unshift(rightPreimage[index]);
        }

        console.log("Updated insertStack:", this.insertStack);
        return [this.currentIndex, this.currentRoot];
    }
}

module.exports = {
    RightMerkleTree
};

async function main() {
    const initRoot = 513; // Initial root value
    const tree = new RightMerkleTree(initRoot);

    console.log("\nInitial root:", tree.currentRoot);

    // Test insertions (16 values)
    const testValues = [
        123, 456, 789, 101, 202, 303, 404, 505,
        606, 707, 808, 909, 111, 222, 333, 444
    ];

    try {
        for (const value of testValues) {
            let [index, root] = await tree.insert(value);
            console.log(`\nInserted ${value}: current index = ${index}, current root = ${root}`);
        }
    } catch (error) {
        console.error("Error during insertion:", error);
    }
}

// Run the main function
main();