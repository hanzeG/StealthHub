const chai = require("chai");
const path = require("path");
const wasm_tester = require("circom_tester").wasm;

const { poseidon2_hash } = require("../src/utils");

describe("Poseidon2 Circuit test", function () {
    let circuit;

    this.timeout(1000000);

    before(async () => {
        circuit = await wasm_tester(path.join(__dirname, "circuits", "poseidon2_3_test.circom"));
    });

    it("Should check constrain of hash([1, 1, 1])", async () => {
        const input = [1, 1, 1];
        const res2 = await poseidon2_hash(input);
        console.log(res2);

        const w = await circuit.calculateWitness({ inputs: input });

        await circuit.assertOut(w, { out: res2 });
        await circuit.checkConstraints(w);
    });
});