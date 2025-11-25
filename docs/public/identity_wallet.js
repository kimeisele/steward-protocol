/**
 * IDENTITY WALLET - Human becomes Agent "HIL"
 * 
 * Critical functions:
 * - generateIdentity() - Creates ECDSA P-256 key pair
 * - signMessage() - Signs every user action
 * - registerWithCity() - Sends public key to Agent City
 * 
 * Security: Keys stored in IndexedDB (XSS resistant per Opus audit)
 */

class IdentityWallet {
    constructor() {
        this.dbName = 'AgentCityWallet';
        this.storeName = 'keys';
        this.dbVersion = 1;
        this.db = null;
    }

    // Initialize DB connection
    async _initDB() {
        if (this.db) return this.db;

        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onerror = (event) => {
                console.error("IdentityWallet: DB error", event);
                reject("Failed to open IdentityWallet DB");
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(this.storeName)) {
                    db.createObjectStore(this.storeName);
                }
            };
        });
    }

    // Generate new identity (run once per browser)
    async generateIdentity() {
        console.log("IdentityWallet: Generating new ECDSA P-256 identity...");
        const keyPair = await crypto.subtle.generateKey(
            { name: "ECDSA", namedCurve: "P-256" },
            false,  // non-extractable for security (private key stays in browser)
            ["sign", "verify"]
        );

        // Export public key for registration
        const publicKey = await crypto.subtle.exportKey("spki", keyPair.publicKey);
        const publicKeyHex = this._arrayBufferToHex(publicKey);

        // Store keys in IndexedDB
        await this._storeKeys(keyPair);
        console.log("IdentityWallet: Identity generated and stored.");

        return { publicKey: publicKeyHex };
    }

    // Check if identity exists
    async hasIdentity() {
        try {
            const keys = await this._getKeys();
            return !!keys;
        } catch (e) {
            return false;
        }
    }

    // Sign message with private key
    async signMessage(message) {
        const keys = await this._getKeys();
        if (!keys) throw new Error("No identity found. Generate one first.");

        const privateKey = keys.privateKey;
        const timestamp = Date.now();

        // Include timestamp in payload to prevent replay attacks
        const payload = JSON.stringify({ message, timestamp });
        const signature = await crypto.subtle.sign(
            { name: "ECDSA", hash: "SHA-256" },
            privateKey,
            new TextEncoder().encode(payload)
        );

        return {
            message,
            timestamp,
            signature: this._arrayBufferToHex(signature)
        };
    }

    // Register with Agent City
    async registerWithCity(apiUrl) {
        let identity;
        if (await this.hasIdentity()) {
            const keys = await this._getKeys();
            const publicKey = await crypto.subtle.exportKey("spki", keys.publicKey);
            identity = { publicKey: this._arrayBufferToHex(publicKey) };
        } else {
            identity = await this.generateIdentity();
        }

        console.log("IdentityWallet: Registering with City at", apiUrl);
        const response = await fetch(`${apiUrl}/v1/register_human`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                agent_id: "HIL",
                public_key: identity.publicKey,
                timestamp: Date.now()
            })
        });

        if (!response.ok) {
            throw new Error(`Registration failed: ${response.statusText}`);
        }

        return response.json();
    }

    // Helper: ArrayBuffer to hex string
    _arrayBufferToHex(buffer) {
        return Array.from(new Uint8Array(buffer))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    }

    // Store keys in IndexedDB
    async _storeKeys(keyPair) {
        const db = await this._initDB();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([this.storeName], "readwrite");
            const store = transaction.objectStore(this.storeName);
            const request = store.put(keyPair, "identity"); // Store as "identity"

            request.onerror = () => reject("Failed to store keys");
            request.onsuccess = () => resolve();
        });
    }

    // Retrieve keys from IndexedDB
    async _getKeys() {
        const db = await this._initDB();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([this.storeName], "readonly");
            const store = transaction.objectStore(this.storeName);
            const request = store.get("identity");

            request.onerror = () => reject("Failed to retrieve keys");
            request.onsuccess = () => resolve(request.result);
        });
    }

    // Retrieve private key (internal use)
    async _getPrivateKey() {
        const keys = await this._getKeys();
        return keys ? keys.privateKey : null;
    }
}
