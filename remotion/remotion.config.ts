import {Config} from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// 用 Playwright 已装好的 chrome-headless-shell，避开 storage.googleapis.com 被墙的下载
Config.setBrowserExecutable(
  "C:/Users/冯兴龙/AppData/Local/ms-playwright/chromium_headless_shell-1208/chrome-headless-shell-win64/chrome-headless-shell.exe"
);
