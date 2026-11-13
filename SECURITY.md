# Security policy

SecureLock is a **university educational project**, not an independently audited or production-ready password manager. **Do not store real passwords or sensitive accounts** in it. The original `securelock.py` prototype stores credentials in plaintext; the encrypted Tkinter application is launched with `python main.py`.

## Reporting a vulnerability

Please report suspected vulnerabilities **privately to the repository maintainer** through GitHub's private vulnerability reporting feature if it is enabled. If that feature is not available, contact the maintainer privately rather than posting an exploit, vault file, credential, or master password in a public issue.

Do not include real credentials, decrypted vault contents, or master passwords in a report. Reproduce issues using fictional test data. Include the affected version/commit, Python/OS versions, clear reproduction steps, and the expected versus actual outcome.

## Supported versions

The current development branch on `main` is the only version under active maintenance. There are no guaranteed support timelines or security-service commitments.

## Known limitations

- Strong master passphrases are essential; an attacker with a copied vault can attempt offline guessing.
- Scrypt/AES-GCM protect stored content, not an unlocked device or memory from malware.
- There is no guaranteed memory erasure, inactivity lock, master-password recovery, concurrent-writer protection, rollback detection, or independent audit.
- Protect encrypted backups and filesystem access; consult [README.md](README.md) and [INTERFACES.md](INTERFACES.md) for detailed limitations.
- The three-attempt GUI login limit does not stop offline guessing.

This policy does not constitute a security certification.
