# HUNT-DRIFT-01 Amendment 3 — analysis (REAL, EXPLORATORY)

Plan `PLAN_AMENDMENT_3.md` 34a16542 (locked). 720 items × 19 arms, depth 0, P-none; one skeleton (user → agent → tool turns, the plant always last). δ = 0.234; template-clustered bootstrap 2000, seed 7101001.

## Primary (A3.1)

Imperatives, wrapper W1 ('A line from something I read'): **I = Δ(own) − Δ(user) = +0.01 [-1.04, +1.10]** → **indeterminate** (predicted negative).

## Δ = Y_quoted − Y_issued per slot (secondary)

+ = the quote pulls less than the issued line.

| slot | W1 imp | W1 int | W2 imp | W2 int |
|---|---|---|---|---|
| own | +1.12 [+0.53, +1.70] | +1.67 [+1.01, +2.33] | -0.12 [-0.59, +0.38] | -0.41 [-0.94, +0.17] |
| user | +1.12 [-0.00, +2.22] | +1.22 [+0.38, +2.01] | +0.79 [-0.17, +1.79] | +0.97 [+0.28, +1.65] |
| tool | +0.46 [-0.20, +1.17] | +1.64 [+1.15, +2.19] | +0.71 [+0.26, +1.20] | +0.97 [+0.63, +1.33] |

## Interactions (secondary)

| contrast | W1 imp | W1 int | W2 imp | W2 int |
|---|---|---|---|---|
| Δ(own) − Δ(user) | +0.01 [-1.04, +1.10] **(primary)** | +0.45 [-0.41, +1.37] | -0.91 [-1.89, +0.04] | -1.38 [-2.06, -0.65] |
| Δ(own) − Δ(tool) | +0.66 [+0.08, +1.23] | +0.03 [-0.49, +0.53] | -0.83 [-1.32, -0.34] | -1.37 [-1.89, -0.83] |
| Δ(user) − Δ(tool) | +0.66 [-0.28, +1.67] | -0.43 [-1.42, +0.55] | +0.08 [-0.88, +1.05] | +0.01 [-0.79, +0.84] |

## Pull of an issued line per slot, at matched distance (secondary)

pull = Y_all-inert − Y_issued (+ = the instruction pulls away from the system target).

| slot | imperative | intention |
|---|---|---|
| own | +1.66 [+1.12, +2.24] | +2.39 [+1.77, +3.06] |
| user | +2.25 [+1.44, +3.08] | +2.01 [+1.39, +2.57] |
| tool | +2.74 [+2.17, +3.33] | +4.17 [+3.48, +4.82] |

Target → readout tokens (median) by arm: own_issued_imp 14, own_issued_int 14, own_W1_imp 14, own_W1_int 14, own_W2_imp 14, own_W2_int 14, user_issued_imp 14, user_issued_int 14, user_W1_imp 14, user_W1_int 14, user_W2_imp 14, user_W2_int 14, tool_issued_imp 14, tool_issued_int 14, tool_W1_imp 15, tool_W1_int 15, tool_W2_imp 15, tool_W2_int 15.

## A3.2 chunk test

1344 rows; (a) full-run chunking = the full run's readouts on 1344; (b) B-a chunking = B-a's on 1344; the two references differ on 476 rows. → **the gap is prefill chunking**.

