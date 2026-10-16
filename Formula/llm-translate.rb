class LlmTranslate < Formula
  desc "Multi-language prompt and response translator for AI coding agents (Antigravity, Claude, Cursor)"
  homepage "https://github.com/sergeypylypyshko/llm-translate"
  url "https://github.com/sergeypylypyshko/llm-translate/archive/refs/tags/v1.3.0.tar.gz"
  license "MIT"

  depends_on "python@3.10"

  def install
    bin.install "tr" => "tr"
    bin.install "ag-tr" => "ag-tr"
    prefix.install Dir["*"]
  end

  test do
    system "#{bin}/tr", "status"
  end
end
