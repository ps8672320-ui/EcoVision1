
const wasteImage = document.getElementById("wasteImage");
const imagePreview = document.getElementById("imagePreview");
const previewPlaceholder = document.getElementById("previewPlaceholder");
const previewButton = document.getElementById("previewButton");
const scannerMessage = document.getElementById("scannerMessage");

const analysisResult = document.getElementById("analysisResult");
const wasteCategory = document.getElementById("wasteCategory");
const confidenceText = document.getElementById("confidenceText");
const confidenceFill = document.getElementById("confidenceFill");
const confidenceBar = document.getElementById("confidenceBar");
const disposalAdvice = document.getElementById("disposalAdvice");

const historyList = document.getElementById("historyList");
const clearHistoryButton = document.getElementById("clearHistoryButton");

let scanHistory = [];

try {
    scanHistory = JSON.parse(
        localStorage.getItem("ecoVisionHistory") || "[]"
    );
    if (!Array.isArray(scanHistory)) scanHistory = [];
} catch {
    scanHistory = [];
}

function renderHistory() {
    if (!historyList) return;

    historyList.replaceChildren();

    if (scanHistory.length === 0) {
        const message = document.createElement("p");
        message.textContent = "No scans yet. Analyse an image to see your history.";
        historyList.appendChild(message);
        return;
    }

    scanHistory.forEach(function (scan) {
        const item = document.createElement("div");
        item.className = "history-item";

        const details = document.createElement("div");
        details.className = "history-details";

        const category = document.createElement("strong");
        category.textContent = scan.category;

        const confidence = document.createElement("p");
        confidence.textContent = "Confidence: " + scan.confidence + "%";

        const date = document.createElement("small");
        date.textContent = scan.date;

        details.append(category, confidence, date);

        const status = document.createElement("span");
        status.className = "history-status";
        status.textContent = "Analysed";

        item.append(details, status);
        historyList.appendChild(item);
    });
}

renderHistory();

if (clearHistoryButton) {
    clearHistoryButton.addEventListener("click", function () {
        scanHistory = [];
        localStorage.removeItem("ecoVisionHistory");
        renderHistory();
    });
}

if (wasteImage) {
    wasteImage.addEventListener("change", function () {
        const file = wasteImage.files[0];
        if (!file) return;

        if (!file.type.startsWith("image/")) {
            scannerMessage.textContent = "Please select a valid image.";
            wasteImage.value = "";
            return;
        }

        if (imagePreview) {
            imagePreview.src = URL.createObjectURL(file);
            imagePreview.style.display = "block";
        }

        if (previewPlaceholder) {
            previewPlaceholder.style.display = "none";
        }

        scannerMessage.textContent = "Image selected. Click Analyse Waste.";
    });
}

if (previewButton) {
    previewButton.addEventListener("click", async function () {
        const file = wasteImage.files[0];

        if (!file) {
            scannerMessage.textContent = "Please select an image first.";
            return;
        }

        previewButton.disabled = true;
        previewButton.textContent = "Analysing...";
        scannerMessage.textContent = "AI is analysing your image. Please wait.";

        const formData = new FormData();
        formData.append("image", file);

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || "Analysis failed.");
            }

            const confidence = Math.max(
                0,
                Math.min(100, Number(result.confidence) || 0)
            );

            wasteCategory.textContent = result.classification;
            confidenceText.textContent = confidence + "%";
            confidenceFill.style.width = confidence + "%";
            confidenceBar.setAttribute("aria-valuenow", confidence);
            disposalAdvice.textContent = result.advice;

            analysisResult.hidden = false;
            scannerMessage.textContent = "Analysis completed successfully!";

            scanHistory.unshift({
                category: result.classification,
                confidence: confidence,
                date: new Date().toLocaleString()
            });

            scanHistory = scanHistory.slice(0, 10);
            localStorage.setItem(
                "ecoVisionHistory",
                JSON.stringify(scanHistory)
            );

            renderHistory();

        } catch (error) {
            scannerMessage.textContent = "Error: " + error.message;
        } finally {
            previewButton.disabled = false;
            previewButton.textContent = "🔍 Analyse Waste";
        }
    });
}
