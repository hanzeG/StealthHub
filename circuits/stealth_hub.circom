pragma circom 2.1.6;

include "utils.circom";
include "poseidon2.circom";

template MultiWithdraw(number, level1, level2) {
    signal input leaves[number];
    
    signal input root1[number];
    signal input pathElements1[number][level1];
    signal input pathIndices1[number][level1];
    
    signal input root2[number];
    signal input pathElements2[number][level2];
    signal input pathIndices2[number][level2];
    
    signal input nullifierHash[number];

    // Merkle tree operations
    signal input receipt; // Not used in computations, included for integrity checks
    signal input relayer;  // Not used in computations, included for integrity checks
    signal input fee;      // Not used in computations, included for integrity checks
    signal input refund;   // Not used in computations, included for integrity checks

    signal output isSpent; // Output signal indicating a successful spend

    // Check leaves existence in the Merkle tree
    component ph0 = MerkleTreeCheckerPoseidon2(DEPTH);
    ph0.leaf <== messageHash;
    ph0.root <== root;
    for (var i = 0; i < DEPTH; i++) {
        ph0.pathElements[i] <== pathElements[i];
        ph0.pathIndices[i] <== pathIndices[i];
    }

    // Verify the preimage of message hash using Poseidon2
    component ph1 = Poseidon2(3,1);
    ph1.inputs[0] <== message[0];
    ph1.inputs[1] <== 1;
    ph1.inputs[2] <== 1;
    messageHash === ph1.out[0];

    // Compute nullifier hash using Poseidon2
    component ph2 = Poseidon2(3,1);
    ph2.inputs[0] <== inv[0];
    ph2.inputs[1] <== message[0];
    ph2.inputs[2] <== 1;
    nullifierHash === ph2.out[0];

    // Add hidden signals to ensure tampering with receipt or fee invalidates the SNARK proof
    // While not strictly necessary, these constraints provide additional security
    // Squares are used to prevent the optimizer from removing these constraints
    signal receiptSquare;
    signal feeSquare;
    signal relayerSquare;
    signal refundSquare;
    receiptSquare <== receipt * receipt;
    feeSquare <== fee * fee;
    relayerSquare <== relayer * relayer;
    refundSquare <== refund * refund;

    // If a valid proof is generated, all constraints above are satisfied; set isSpent to 1
    isSpent <== 1;
}

// Bob spend their own utxo to mint new one for Alice (no new external deposit)
template MultiTransfer(CHUNK_SIZE, CHUNK_NUMBER, BITS, DEPTH) {
    signal input mint_message[CHUNK_NUMBER]; // private signal
    signal input mint_N[CHUNK_NUMBER]; // private signal
    signal input mint_exp; // public signal: exp
    
    // spend template inputs
    signal input spend_message[CHUNK_NUMBER];  // Private signal: decrypted message
    signal input spend_inv[CHUNK_NUMBER]; // Private signal: inv
    signal input spend_messageHash;  // Public signal: message hash (commitment)
    signal input spend_nullifierHash;  // Public signal: nullifier hash
    
    // Merkle tree operations
    signal input root;                 // Public signal: Merkle tree root
    signal input pathElements[DEPTH];  // Merkle tree path elements
    signal input pathIndices[DEPTH];   // Merkle tree path indices
    signal input receipt; // Not used in computations, included for integrity checks
    signal input relayer;  // Not used in computations, included for integrity checks
    signal input fee;      // Not used in computations, included for integrity checks
    signal input refund;   // Not used in computations, included for integrity checks
    
    signal output out[CHUNK_NUMBER + 1];  // public signal, new ciphertext[CHUNK_NUMBER] and commitment for UTXO

    // spend old UTXO
    component sp = Spend(CHUNK_SIZE, CHUNK_NUMBER, DEPTH);
    sp.messageHash <== spend_messageHash;
    sp.nullifierHash <== spend_nullifierHash;
    for (var i = 0; i < CHUNK_NUMBER; i++) {
        sp.message[i] <== spend_message[i];
        sp.inv[i] <== spend_inv[i];
    }
    sp.root <== root;
    sp.receipt <== receipt;
    sp.relayer <== relayer;
    sp.fee <== fee;
    sp.refund <== refund;
    for (var i = 0; i < DEPTH; i++) {
        sp.pathElements[i] <== pathElements[i];
        sp.pathIndices[i] <== pathIndices[i];
    }

    sp.isSpent === 1;

    // pow mod to generate new commitment (ciphertext)
    component pm = PowerModAnyExp(CHUNK_SIZE, CHUNK_NUMBER, BITS);

    for (var i = 0; i < CHUNK_NUMBER; i++) {
        pm.base[i] <== mint_message[i];
        pm.modulus[i] <== mint_N[i];
    }
    pm.exp <== mint_exp;
    
    for (var i = 0; i < CHUNK_NUMBER; i++) {
        out[i] <== pm.out[i];
    }

    // Compute message (secret) hash (commitment) using Poseidon2
    component ph = Poseidon2(3,1);
    ph.inputs[0] <== mint_message[0];
    ph.inputs[1] <== 1;
    ph.inputs[2] <== 1;
    out[CHUNK_NUMBER] <== ph.out[0];
}