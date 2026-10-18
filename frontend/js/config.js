"use strict";

async function loadApiConfig(inputId, onError) {
    try {
        const response = await fetch("/config.txt", { cache: "no-store" });
        if (!response.ok) throw new Error("Configuration is unavailable");

        const match = (await response.text()).match(/^API_BASE_URL=(.*)$/m);
        if (!match || !match[1].trim()) throw new Error("API_BASE_URL is missing");

        const configuredUrl = match[1].trim();
        const url = new URL(configuredUrl);
        if (!["http:", "https:"].includes(url.protocol) || !url.hostname || url.username || url.password || url.search || url.hash) {
            throw new Error("API_BASE_URL is invalid");
        }

        const input = document.getElementById(inputId);
        if (!input.value.trim()) input.value = configuredUrl.replace(/\/$/, "");
    } catch {
        onError("Không tải được cấu hình API. Kiểm tra frontend/.env và khởi động lại frontend, hoặc nhập địa chỉ API thủ công.");
    }
}
