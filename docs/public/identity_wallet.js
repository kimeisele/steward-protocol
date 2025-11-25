/**
 * 👁️ AJNA CHAKRA: VibeChat Identity Wallet
 * GAD-3000 Standard: ECDSA P-256 Signature Layer
 */

const DB_NAME = "VibeChat_Identity_v1";
const STORE_NAME = "keypair";

class IdentityWallet {
    constructor() {
        this.keyPair = null;
        this.publicKeyHex = null;
        this.agentId = "HIL_OPERATOR";
        this.db = null;
        console.log("🧩 Wallet Class Instantiated");
    }

    async init() {
        console.log("👁️ Opening Third Eye (Identity Wallet)...");
        try {
            await this._openDB();

            const existing = await this._getKey();
            if (existing) {
                console.log("✅ Identity Loaded from Storage");
                this.keyPair = existing;
            } else {
                console.log("⚡ Generating New Genesis Identity...");
                this.keyPair = await this._generateKeys();
                await this._saveKey(this.keyPair);
            }

            this.publicKeyHex = await this._exportKey(this.keyPair.publicKey);
            console.log("🔑 Public Key Available");
            return this.publicKeyHex;
        } catch (e) {
            console.error("CRITICAL WALLET FAILURE:", e);
            throw e;
        }
    }

    async signPayload(message) {
        if (!this.keyPair) throw new Error("Wallet not initialized");

        const encoder = new TextEncoder();
        const data = encoder.encode(message);

        const signature = await window.crypto.subtle.sign(
            { name: "ECDSA", hash: { name: "SHA-256" } },
            this.keyPair.privateKey,
            data
        );

        return {
            message: message,
            signature: this._buf2hex(signature),
            public_key: this.publicKeyHex,
            agent_id: this.agentId,
            timestamp: Date.now()
        };
    }

    // --- INTERNAL CRYPTO PLUMBING ---

    async _generateKeys() {
        return window.crypto.subtle.generateKey(
            { name: "ECDSA", namedCurve: "P-256" },
            false,
            ["sign", "verify"]
        );
    }

    async _exportKey(key) {
        const exported = await window.crypto.subtle.exportKey("spki", key);
        return this._buf2hex(exported);
    }

    _buf2hex(buffer) {
        return [...new Uint8Array(buffer)]
            .map(x => x.toString(16).padStart(2, '0'))
            .join('');
    }

    // --- INDEXED DB STORAGE ---

    _openDB() {
        return new Promise((resolve, reject) => {
            const req = indexedDB.open(DB_NAME, 1);
            req.onupgradeneeded = e => {
                e.target.result.createObjectStore(STORE_NAME);
            };
            req.onsuccess = () => { this.db = req.result; resolve(); };
            req.onerror = (e) => reject("DB Open Error: " + e.target.error);
        });
    }

    _getKey() {
        return new Promise((resolve, reject) => {
            if (!this.db) return reject("DB not open");
            const tx = this.db.transaction(STORE_NAME, "readonly");
            const req = tx.objectStore(STORE_NAME).get("hil_key");
            req.onsuccess = () => resolve(req.result);
            req.onerror = () => reject(req.error);
        });
    }

    _saveKey(keys) {
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction(STORE_NAME, "readwrite");
            tx.objectStore(STORE_NAME).put(keys, "hil_key");
            tx.oncomplete = resolve;
            tx.onerror = () => reject(tx.error);
        });
    }
}

// FORCE GLOBAL ASSIGNMENT
console.log("⚡ Attaching Wallet to Window...");
window.wallet = new IdentityWallet();
console.log("✅ Wallet Attached:", window.wallet);
