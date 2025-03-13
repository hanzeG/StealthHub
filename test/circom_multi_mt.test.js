const chai = require("chai");
const path = require("path");
const fs = require("fs");
const wasm_tester = require("circom_tester").wasm;
const { MT } = require("../src/mt");
const { poseidon2_hash } = require("../src/utils");

// Define the constant 'zero' value used for the Merkle tree initialisation.
const zero = 513;

/**
 * Runs a test suite for a specified circom circuit.
 * @param {string} circuitFile - The filename of the circom circuit.
 * @param {number} number - The number of leaves to be processed.
 * @param {number} mt1_depth - The depth of the first-layer Merkle tree.
 * @param {number} mt2_depth - The depth of the second-layer Merkle trees.
 */
function runTest(circuitFile, number, mt1_depth, mt2_depth) {
    describe(`Testing ${circuitFile} (number = ${number}, mt1_depth = ${mt1_depth}, mt2_depth = ${mt2_depth})`, function () {
        let circuit;
        let mt1;
        let mt2 = new Array(number);
        let leaves = new Array(number);

        let root1 = new Array(number);
        let root2 = new Array(number);

        let pathElements1 = new Array(number);
        let pathIndices1 = new Array(number);

        let pathElements2 = new Array(number);
        let pathIndices2 = new Array(number); // Corrected initialisation to use 'number' as size

        // Increase timeout to allow for circuit compilation and computation.
        this.timeout(1000000);

        // Before running tests, load the circuit and initialise Merkle trees.
        before(async () => {
            console.log(`Loading circuit file: ${circuitFile}`);
            // Load the compiled circom circuit.
            circuit = await wasm_tester(path.join(__dirname, "circuits", circuitFile));
            console.log(`Circuit ${circuitFile} loaded successfully.`);

            // Build the first-layer Merkle tree.
            console.log(`Building first-layer Merkle tree with depth ${mt1_depth}`);
            mt1 = await MT.build(zero, mt1_depth);
            console.log("First-layer Merkle tree initialised.");

            // Build an array of second-layer Merkle trees (one per leaf).
            for (let i = 0; i < number; i++) {
                console.log(`Building second-layer Merkle tree ${i + 1}/${number} with depth ${mt2_depth}`);
                mt2[i] = await MT.build(zero, mt2_depth);
            }
            console.log("All second-layer Merkle trees initialised.");
        });

        // Test to check that valid proofs are generated for all leaves.
        it(`should generate valid proofs for ${number} leaves with layer1 depth ${mt1_depth} and layer 2 depth ${mt2_depth}`, async () => {
            for (let i = 0; i < number; i++) {
                console.log(`\nProcessing leaf ${i + 1} of ${number}`);

                // Generate a random preimage and compute its Poseidon2 hash.
                const preimage = [Math.floor(Math.random() * 100), 1, 1];
                console.log(`Leaf ${i + 1} preimage: ${preimage}`);
                const hashResult = await poseidon2_hash(preimage);
                leaves[i] = hashResult[0];
                console.log(`Computed hash for leaf ${i + 1}: ${leaves[i]}`);

                // Determine a random number of insertions for the second-layer Merkle tree.
                const randomInsert = Math.floor(Math.random() * 4); // 4 is used for testing; in practice, this should be less than 2 ** mt2_depth - 1.
                console.log(`Random insertion count for second-layer tree ${i + 1}: ${randomInsert}`);

                let mt2_proof;
                // Insert the leaf into the second-layer Merkle tree repeatedly.
                for (let j = 0; j <= randomInsert; j++) {
                    mt2_proof = await mt2[i].insert(leaves[i]);
                }
                // Capture the resulting root and proof components from the second layer.
                root2[i] = mt2_proof[0];
                pathElements2[i] = mt2_proof[1][0];
                pathIndices2[i] = mt2_proof[1][1];
                console.log(`Second-layer tree ${i + 1} root: ${root2[i]}`);
                console.log(`Second-layer proof for leaf ${i + 1}: path elements ${pathElements2[i]}, path indices ${pathIndices2[i]}`);

                // Insert the root of the second-layer tree into the first-layer Merkle tree.
                const mt1_proof = await mt1.insert(mt2[i].root);
                // Capture the resulting root and proof components from the first layer.
                root1[i] = mt1_proof[0];
                pathElements1[i] = mt1_proof[1][0];
                pathIndices1[i] = mt1_proof[1][1];
                console.log(`First-layer tree updated with second-layer root from tree ${i + 1}`);
                console.log(`First-layer proof for leaf ${i + 1}: path elements ${pathElements1[i]}, path indices ${pathIndices1[i]}`);
            }

            // Construct the input object for the circom circuit.
            const input = {
                leaves: leaves,
                root1: root1,
                pathElements1: pathElements1,
                pathIndices1: pathIndices1,
                root2: root2,
                pathElements2: pathElements2,
                pathIndices2: pathIndices2,
            };
            console.log("\nFinal input for circuit:", input);

            // Save the input object to a JSON file at relative path "../circuit_input"
            // with the same name as the circuit file.
            const baseName = path.basename(circuitFile, ".circom");
            const outputPath = path.join(__dirname, "../circuit_input", baseName + ".json");
            fs.writeFileSync(outputPath, JSON.stringify(input, null, 2));
            console.log(`Input saved to ${outputPath}`);

            // Calculate the witness and verify that all circuit constraints are satisfied.
            console.log("Calculating witness...");
            const witness = await circuit.calculateWitness(input);
            console.log("Witness calculated, checking constraints...");
            await circuit.checkConstraints(witness);
            console.log("All constraints satisfied for this test.\n");
        });
    });
}

// Execute the test suites for various circuit configurations.
runTest("multi_merkle_4_4_4.circom", 4, 4, 4);
runTest("multi_merkle_5_5_5.circom", 5, 5, 5);
runTest("multi_merkle_6_6_6.circom", 6, 6, 6);
runTest("multi_merkle_7_7_7.circom", 7, 7, 7);
runTest("multi_merkle_8_8_8.circom", 8, 8, 8);
runTest("multi_merkle_9_9_9.circom", 9, 9, 9);

// runTest("multi_merkle_10_20_10.circom", 10, 20, 10);
// runTest("multi_merkle_11_20_10.circom", 11, 20, 10);
// runTest("multi_merkle_12_20_10.circom", 12, 20, 10);
// runTest("multi_merkle_10_21_10.circom", 10, 21, 10);
// runTest("multi_merkle_10_22_10.circom", 10, 22, 10);
// runTest("multi_merkle_10_20_11.circom", 10, 20, 11);
// runTest("multi_merkle_10_20_12.circom", 10, 20, 12);