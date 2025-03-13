import * as eccryptoJS from 'eccrypto-js';
import {
    getSharedSecret as nobleGetSharedSecret,
    utils as nobleUtils,
    getPublicKey,
    Point,
    CURVE,
} from '@noble/secp256k1';

async function main() {
    // Generate an ECC key pair
    const keyPair = eccryptoJS.generateKeyPair();

    // Define the message to encrypt and convert it to a buffer
    const str = 'test message to encrypt';
    const msg = eccryptoJS.utf8ToBuffer(str);

    // Encrypt the message using the public key
    const encrypted = await eccryptoJS.encrypt(keyPair.publicKey, msg);

    // Decrypt the ciphertext using the private key
    const decrypted = await eccryptoJS.decrypt(keyPair.privateKey, encrypted);

    // Verify and output the result
    console.log('Original message:', str);
    console.log('Decrypted message:', decrypted.toString());
    console.log('Decryption successful:', decrypted.toString() === str);

}

// Run the main function and catch any errors
main().catch((error) => {
    console.error('Error during execution:', error);
});