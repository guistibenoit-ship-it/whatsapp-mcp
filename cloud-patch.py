"""Apply narrowly scoped patches to the upstream Go bridge during image build."""
from pathlib import Path

p = Path('main.go')
s = p.read_text()
patches = [
    ('sqlstore.New("sqlite3",', 'sqlstore.New(context.Background(), "sqlite3",'),
    ('container.GetFirstDevice()', 'container.GetFirstDevice(context.Background())'),
    ('client.Download(downloader)', 'client.Download(context.Background(), downloader)'),
    ('client.GetGroupInfo(jid)', 'client.GetGroupInfo(context.Background(), jid)'),
    ('client.Store.Contacts.GetContact(jid)', 'client.Store.Contacts.GetContact(context.Background(), jid)'),
    ('"go.mau.fi/whatsmeow/store/sqlstore"',
     '"go.mau.fi/whatsmeow/store/sqlstore"\n\t"go.mau.fi/whatsmeow/store"'),
    ('client := whatsmeow.NewClient(deviceStore, logger)',
     '''latestVersion, versionErr := whatsmeow.GetLatestVersion(context.Background(), &http.Client{Timeout: 30 * time.Second})
    if versionErr != nil {
        logger.Errorf("Cannot fetch current WhatsApp Web version: %v", versionErr)
        return
    }
    store.SetWAVersion(*latestVersion)
    logger.Infof("Using current WhatsApp Web version: %s", latestVersion.String())
    client := whatsmeow.NewClient(deviceStore, logger)'''),
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
