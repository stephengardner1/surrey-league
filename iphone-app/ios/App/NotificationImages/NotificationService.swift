// Adds the picture on the right of a Surrey League notification:
// a runner's portrait (downloaded from slarchive.org) or a club singlet (built in).
// The back office sends "image": { "type": "portrait", "file": "jack-kavanagh", "club": "HOL" }
// or { "type": "singlet", "club": "BEL" }. Corrections have no image.
import UserNotifications

class NotificationService: UNNotificationServiceExtension {
    private var contentHandler: ((UNNotificationContent) -> Void)?
    private var content: UNMutableNotificationContent?

    override func didReceive(_ request: UNNotificationRequest, withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void) {
        self.contentHandler = contentHandler
        guard let content = request.content.mutableCopy() as? UNMutableNotificationContent else {
            contentHandler(request.content); return
        }
        self.content = content
        guard let image = content.userInfo["image"] as? [String: Any], let type = image["type"] as? String else {
            contentHandler(content); return
        }
        let club = image["club"] as? String ?? ""

        if type == "portrait", let file = image["file"] as? String,
           let safe = file.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed),
           let url = URL(string: "https://slarchive.org/portraits/og/athletes/\(safe).png") {
            let task = URLSession.shared.downloadTask(with: url) { [weak self] location, response, _ in
                guard let self = self else { return }
                if let location = location, (response as? HTTPURLResponse)?.statusCode == 200 {
                    self.attach(from: location, name: "portrait.png")
                } else {
                    self.attachSinglet(club)
                }
                self.finish()
            }
            task.resume()
        } else {
            attachSinglet(club)
            finish()
        }
    }

    // iOS gives the extension a few seconds; if the download is slow, send it without the picture
    override func serviceExtensionTimeWillExpire() {
        finish()
    }

    private func finish() {
        guard let handler = contentHandler, let content = content else { return }
        contentHandler = nil
        handler(content)
    }

    private func attachSinglet(_ club: String) {
        let name = club.replacingOccurrences(of: "/", with: "").replacingOccurrences(of: "&", with: "and")
        let bundle = Bundle(for: NotificationService.self)
        guard let url = bundle.url(forResource: "singlet-\(name)", withExtension: "png")
                ?? bundle.url(forResource: "singlet-_GENERIC", withExtension: "png") else { return }
        attach(from: url, name: "singlet.png")
    }

    // Notification pictures must be a file the system can take over, so copy it somewhere temporary first
    private func attach(from source: URL, name: String) {
        let dir = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString, isDirectory: true)
        do {
            try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
            let dest = dir.appendingPathComponent(name)
            try FileManager.default.copyItem(at: source, to: dest)
            let attachment = try UNNotificationAttachment(identifier: "picture", url: dest, options: nil)
            content?.attachments = [attachment]
        } catch {
            // No picture: the notification still arrives
        }
    }
}
