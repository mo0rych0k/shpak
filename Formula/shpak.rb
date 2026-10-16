class Shpak < Formula
  desc "Zero-glitch transparent PTY wrapper & translator for AI coding CLIs (Antigravity, Claude, Codex, Cursor)"
  homepage "https://github.com/mo0rych0k/shpak"
  url "https://github.com/mo0rych0k/shpak/archive/refs/tags/v3.0.0.tar.gz"
  head "https://github.com/mo0rych0k/shpak.git", branch: "main"
  license "MIT"

  depends_on "python@3.10"

  def install
    bin.install "shpak-cli" => "spk"
    bin.install_symlink bin/"spk" => "shpak"
    bin.install "agy-shpak" => "agy-spk"
    bin.install_symlink bin/"agy-spk" => "agy-shpak"
    bin.install_symlink bin/"agy-spk" => "claude-spk"
    bin.install_symlink bin/"agy-spk" => "claude-shpak"
    bin.install_symlink bin/"agy-spk" => "codex-spk"
    bin.install_symlink bin/"agy-spk" => "codex-shpak"
    bin.install_symlink bin/"agy-spk" => "cursor-spk"
    bin.install_symlink bin/"agy-spk" => "cursor-shpak"
    prefix.install Dir["*"]
  end

  test do
    system "#{bin}/spk", "status"
  end
end
