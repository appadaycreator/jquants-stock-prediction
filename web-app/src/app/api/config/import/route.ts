import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { execFile } from "child_process";

export const dynamic = "force-static";

function runValidator(configDirAbs: string): Promise<{ ok: boolean; stdout: string }>{
  return new Promise((resolve) => {
    const pythonPath = process.env.VIRTUAL_ENV
      ? path.join(process.env.VIRTUAL_ENV, "bin", "python")
      : "python3";
    const scriptPath = path.join(process.cwd(), "tools", "validate_config_dir.py");
    execFile(pythonPath, [scriptPath, configDirAbs], (error, stdout) => {
      resolve({ ok: !error, stdout: stdout?.toString() || "" });
    });
  });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const config: Record<string, string | null> = body?.config || {};
    const env: Record<string, string | null> = body?.env || {};

    // 一時ディレクトリに書き出して検証
    const tmpDir = path.join(process.cwd(), ".tmp_config_import");
    if (!fs.existsSync(tmpDir)) fs.mkdirSync(tmpDir, { recursive: true });
    const files = ["core.yaml", "api.yaml", "data.yaml", "models.yaml"];
    for (const f of files) {
      const content = config[f];
      if (typeof content === "string") {
        fs.writeFileSync(path.join(tmpDir, f), content, "utf-8");
      }
    }

    const validation = await runValidator(tmpDir);
    let parsed: any = {};
    try { parsed = JSON.parse(validation.stdout || "{}"); } catch {}
    if (!parsed?.summary?.is_valid) {
      return NextResponse.json({ ok: false, validation: parsed }, { status: 400 });
    }

    // 検証OKなら本番パスへ保存
    const configDir = path.join(process.cwd(), "config");
    if (!fs.existsSync(configDir)) fs.mkdirSync(configDir, { recursive: true });
    for (const f of files) {
      const content = config[f];
      if (typeof content === "string") {
        fs.writeFileSync(path.join(configDir, f), content, "utf-8");
      }
    }

    // .env / .env.local はそのまま文字列で上書き（任意）
    const envMap: Record<string, string | null> = env || {};
    for (const name of Object.keys(envMap)) {
      const val = envMap[name];
      if (typeof val === "string") {
        fs.writeFileSync(path.join(process.cwd(), name), val, "utf-8");
      }
    }

    return NextResponse.json({ ok: true, validation: parsed });
  } catch (e: any) {
    return NextResponse.json({ ok: false, error: String(e?.message || e) }, { status: 500 });
  } finally {
    try {
      const tmpDir = path.join(process.cwd(), ".tmp_config_import");
      if (fs.existsSync(tmpDir)) {
        for (const f of fs.readdirSync(tmpDir)) {
          fs.unlinkSync(path.join(tmpDir, f));
        }
        fs.rmdirSync(tmpDir);
      }
    } catch {}
  }
}


