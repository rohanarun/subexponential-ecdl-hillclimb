# Non-claims

This repository is a research harness around a conditional paper. It does not
claim any of the following.

## Cryptanalytic claims

- **No attack on P-256, P-521, Ed25519, secp256k1, or any deployed curve.**
  The paper's saving only applies to networks of size at least $2^{2^{17}}$ ($2^{131,072}$)
  with base parameter $u_0 = \lfloor b / 2^{17} \rfloor$; the result is asymptotic.
- **No key recovery, no signature forgery, no protocol break.**
- **No claim that the algorithm is practical**, implementable at cryptographic
  scale, or faster than Pollard's rho for any real parameter set.
- **No world record.** This repository does not submit to any ECDL challenge.

## Mathematical claims

- **No unconditional proof of Theorem 4.** `C14` is conditional on `C2`
  (OpenAI's Theorem D.1) and the open lemmas `C3`-`C13`.
- **No independent verification of Theorem D.1.** `C17` is open. The paper's
  authors say they did not verify it, and neither has this repository.
- **No claim that the paper is peer-reviewed.** It is a preprint.
- **No claim that the toy tests generalize.** `tested` means bounded or
  exhaustive at the stated size, never "proved for all parameters".
- **No claim that the table encodings meet the paper's degree bounds.** They are
  semantic oracles, explicitly marked `B1` and `B2`.

## Engineering claims

- **No production cryptography.** The curve arithmetic is affine, naive, and
  intended for tiny fields.
- **No constant-time guarantees.** The code is not side-channel resistant.
- **No claim that the task runner is a secure sandbox.** It runs local commands.
  Isolation, credentials, and provider sandboxing are out of scope for this
  repository.
- **No claim that an agent's self-report is evidence.** Only the verifier and
  the committed artifact count.

## If you want to make a stronger claim

1. Close `C17` with a proof or a concrete refutation of Theorem D.1.
2. Close `C3`-`C13` with Lean proofs or exhaustive checks at the stated bounds.
3. Keep `C14` marked `conditional` until every dependency is `proved`.
4. Add a new claim with its own evidence; do not silently upgrade an existing
   status.
