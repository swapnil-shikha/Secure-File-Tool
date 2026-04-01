key = "monarchy"
text = "instruments"

# 1. Generate 5x5 Matrix
chars = dict.fromkeys(key.lower().replace("j", "i") + "abcdefghiklmnopqrstuvwxyz")
matrix = [list(chars)[i:i+5] for i in range(0, 25, 5)]

# 2. Prepare Plaintext
pt, i, text = "", 0, text.lower().replace("j", "i")
while i < len(text):
    pt += text[i]
    if i + 1 < len(text) and text[i] != text[i+1]:
        pt += text[i+1]; i += 2
    else:
        pt += "x"; i += 1
if len(pt) % 2: pt += "x"

# 3. Encrypt
def pos(char): return next((r, c) for r, row in enumerate(matrix) for c, x in enumerate(row) if x == char)

enc = ""
for i in range(0, len(pt), 2):
    r1, c1, r2, c2 = *pos(pt[i]), *pos(pt[i+1])
    if r1 == r2: enc += matrix[r1][(c1+1)%5] + matrix[r2][(c2+1)%5]
    elif c1 == c2: enc += matrix[(r1+1)%5][c1] + matrix[(r2+1)%5][c2]
    else: enc += matrix[r1][c2] + matrix[r2][c1]

print("Matrix:", *matrix, sep="\n")
print(f"Plain: {text}\nPrepared: {pt}\nCipher: {enc}")
