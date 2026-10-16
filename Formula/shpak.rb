class Shpak < Formula
  desc "Zero-glitch transparent PTY wrapper & translator for AI coding CLIs (Antigravity, Claude, Codex, Cursor)"
  homepage "https://github.com/mo0rych0k/shpak"
  url "https://github.com/mo0rych0k/shpak/archive/refs/tags/v3.0.1.tar.gz"
  sha256 "36a18ccb7186c9cbe53211cdb08ba1af4ba1456da9f8b51579a80f8fee56f3a7"
  head "https://github.com/mo0rych0k/shpak.git", branch: "main"
  license "MIT"

  uses_from_macos "python"

  def install
    libexec.install Dir["*"]

    bin.install_symlink libexec/"shpak-cli" => "spk"
    bin.install_symlink libexec/"shpak-cli" => "shpak"
    bin.install_symlink libexec/"agy-shpak" => "agy-spk"
    bin.install_symlink libexec/"agy-shpak" => "agy-shpak"
    bin.install_symlink libexec/"agy-shpak" => "claude-spk"
    bin.install_symlink libexec/"agy-shpak" => "claude-shpak"
    bin.install_symlink libexec/"agy-shpak" => "codex-spk"
    bin.install_symlink libexec/"agy-shpak" => "codex-shpak"
    bin.install_symlink libexec/"agy-shpak" => "cursor-spk"
    bin.install_symlink libexec/"agy-shpak" => "cursor-shpak"
  end

  test do
    system "#{bin}/spk", "status"
  end
end
