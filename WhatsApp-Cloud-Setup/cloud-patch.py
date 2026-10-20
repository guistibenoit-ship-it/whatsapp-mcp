"""Apply narrowly scoped patches to the upstream Go bridge during image build."""
from pathlib import Path

p = Path('main.go')
s = p.read_text()
patches = [
    ('"github.com/mdp/qrterminal"', ''),
    ('qrterminal.GenerateHalfBlock(evt.Code, qrterminal.L, os.Stdout)',
     'if err := os.WriteFile("/data/qr.txt", []byte(evt.Code), 0600); err != nil { logger.Errorf("Cannot save pairing QR") }'),
    ('} else if evt.Event == "success" {',
     '} else if evt.Event == "success" {\n                os.Remove("/data/qr.txt")'),
    ('serverAddr := fmt.Sprintf(":%d", port)',
     'serverAddr := fmt.Sprintf("127.0.0.1:%d", port)'),
    ('localPath = fmt.Sprintf("%s/%s", chatDir, filename)',
     'filename = filepath.Base(messageID) + "_" + filepath.Base(filename)\n\tlocalPath = filepath.Join(chatDir, filename)'),
]
for old, new in patches:
    if s.count(old) != 1:
        raise RuntimeError('Upstream changed; review cloud patch before deployment')
    s = s.replace(old, new)
p.write_text(s)
