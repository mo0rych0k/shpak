class Shpak < Formula
  desc "Zero-glitch transparent PTY wrapper & translator for AI coding CLIs (Antigravity, Claude, Codex, Cursor)"
  homepage "https://github.com/mo0rych0k/shpak"
  url "https://github.com/mo0rych0k/shpak/archive/refs/tags/v3.0.0.tar.gz"
  sha256 "61c6ab32c832e7f9131fe1e77d39fa6021069f6652aecb4a298aad1eb1adcfcd"
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
