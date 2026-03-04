export default {
    async fetch(request, env) {
        const API_KEY = env.API_KEY;
        const url = new URL(request.url);
        const auth = request.headers.get("Authorization");

        // 🔐 Simple API key check
        if (auth !== `Bearer ${API_KEY}`) {
            return json({ error: "Unauthorized" }, 401);
        }

        // 🚫 Only allow POST requests to /
        if (request.method !== "POST" || url.pathname !== "/") {
            return json({ error: "Not allowed" }, 405);
        }

        try {
            const { prompt, model, aspect_ratio } = await request.json();

            if (!prompt) return json({ error: "Prompt is required" }, 400);

            // 🎨 Supported Cloudflare Workers AI models
            const supportedModels = {
                "sdxl-base": "@cf/stabilityai/stable-diffusion-xl-base-1.0",
                "sdxl-lightning": "@cf/bytedance/stable-diffusion-xl-lightning",
                "dreamshaper": "@cf/lykon/dreamshaper-8-lcm",
                "ux1-schnell": "@cf/blackforestlabs/ux-1-schnell",
                "sd15-img2img": "@cf/runwayml/stable-diffusion-v1-5-img2img",
                "sd15-inpainting": "@cf/runwayml/stable-diffusion-v1-5-inpainting",
                "flux-schnell": "@cf/black-forest-labs/flux-1-schnell"
            };

            // 🎯 Select model (default to SDXL Base)
            const selectedModel = supportedModels[model] || supportedModels["sdxl-base"];

            // 📐 Aspect ratio handling (Cloudflare models have fixed dimensions)
            let dimensions = { width: 1024, height: 1024 }; // Default 1:1

            if (aspect_ratio) {
                switch (aspect_ratio) {
                    case "16:9":
                        dimensions = { width: 1344, height: 768 };
                        break;
                    case "9:16":
                        dimensions = { width: 768, height: 1344 };
                        break;
                    case "1:1":
                    default:
                        dimensions = { width: 1024, height: 1024 };
                        break;
                }
            }

            console.log(`🎨 Generating image with model: ${selectedModel}`);
            console.log(`📐 Dimensions: ${dimensions.width}x${dimensions.height}`);
            console.log(`💬 Prompt: ${prompt.substring(0, 100)}...`);

            // 🧠 Generate image from prompt
            const payload = { prompt };

            // Add dimensions for models that support them
            if (selectedModel.includes("stable-diffusion")) {
                payload.width = dimensions.width;
                payload.height = dimensions.height;
            }

            const result = await env.AI.run(selectedModel, payload);

            return new Response(result, {
                headers: {
                    "Content-Type": "image/png",
                    "X-Model-Used": selectedModel,
                    "X-Dimensions": `${dimensions.width}x${dimensions.height}`
                },
            });
        } catch (err) {
            console.error("❌ Generation error:", err);
            return json({
                error: "Failed to generate image",
                details: err.message,
                supported_models: [
                    "sdxl-base",
                    "sdxl-lightning",
                    "dreamshaper",
                    "ux1-schnell",
                    "sd15-img2img",
                    "sd15-inpainting",
                    "flux-schnell"
                ]
            }, 500);
        }
    },
};

// 📦 Function to return JSON responses
function json(data, status = 200) {
    return new Response(JSON.stringify(data), {
        status,
        headers: { "Content-Type": "application/json" },
    });
}
