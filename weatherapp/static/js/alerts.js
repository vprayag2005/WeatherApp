(function () {
    const config = window.statewiseAlertsConfig;
    if (!config) {
        return;
    }

    const daySelect = document.getElementById("alert-day-select");
    const sourceChip = document.getElementById("alerts-source-chip");
    const summaryGrid = document.getElementById("alert-summary-grid");
    const alertsList = document.getElementById("alerts-list");

    const state = {
        payload: null,
        selectedDay: String(config.defaultDay || 1),
    };

    function formatTimestamp(value) {
        if (!value) {
            return "Not available";
        }

        const date = new Date(value);
        if (Number.isNaN(date.getTime())) {
            return value;
        }

        return new Intl.DateTimeFormat("en-IN", {
            dateStyle: "medium",
            timeStyle: "short",
        }).format(date);
    }



    function refreshMapImage() {
        if (!state.payload) {
            return;
        }
        const imgElement = document.getElementById("imd-alert-image");
        if (imgElement) {
            const images = state.payload.metadata.alert_images || {};
            const imageUrl = images[state.selectedDay];
            if (imageUrl) {
                imgElement.src = imageUrl;
                imgElement.style.display = "block";
            } else {
                imgElement.style.display = "none";
            }
        }
    }

    function renderDaySelect() {
        if (!daySelect || !state.payload) {
            return;
        }

        daySelect.innerHTML = state.payload.metadata.available_days
            .map((item) => `<option value="${item.value}">${item.label}</option>`)
            .join("");
        daySelect.value = state.selectedDay;
    }



    function renderSummary() {
        if (!summaryGrid || !state.payload) {
            return;
        }

        const counts = { 1: 0, 2: 0, 3: 0, 4: 0 };

        state.payload.features.forEach((feature) => {
            const code =
                feature.properties.day_details[state.selectedDay].severity.code;
            counts[code] = (counts[code] || 0) + 1;
        });

        summaryGrid.innerHTML = `
            <div class="summary-card">
                <strong>${state.payload.metadata.total_subdivisions}</strong>
                <span>Total subdivisions tracked</span>
            </div>
            <div class="summary-card">
                <strong>${counts[4] || 0}</strong>
                <span>Warning areas</span>
            </div>
            <div class="summary-card">
                <strong>${counts[3] || 0}</strong>
                <span>Alert areas</span>
            </div>
            <div class="summary-card">
                <strong>${counts[2] || 0}</strong>
                <span>Watch areas</span>
            </div>
        `;
    }



    function renderAlertsList() {
        if (!alertsList || !state.payload) {
            return;
        }

        const cards = [...state.payload.features].sort((left, right) => {
            const leftSeverity =
                left.properties.day_details[state.selectedDay].severity.rank;
            const rightSeverity =
                right.properties.day_details[state.selectedDay].severity.rank;

            if (leftSeverity !== rightSeverity) {
                return rightSeverity - leftSeverity;
            }

            return left.properties.subdivision_name.localeCompare(
                right.properties.subdivision_name
            );
        });

        alertsList.innerHTML = cards
            .map((feature) => {
                const details = feature.properties.day_details[state.selectedDay];
                const warningMarkup = details.warning_summary
                    .slice(0, 3)
                    .map((label) => `<span>${label}</span>`)
                    .join("");

                return `
                    <button
                        type="button"
                        data-subdivision="${feature.properties.subdivision_slug}"
                        style="cursor: default;"
                    >
                        <div class="alert-list-head">
                            <h3>${feature.properties.subdivision_name}</h3>
                            <span class="severity-badge" style="background:${details.severity.hex};">
                                ${details.severity.label}
                            </span>
                        </div>
                        <p class="alert-list-copy">
                            ${details.has_warning ? "Latest active warning set from IMD." : "No active warning for this forecast day."}
                        </p>
                        <div class="alert-list-warnings">${warningMarkup}</div>
                    </button>
                `;
            })
            .join("");
    }

    function renderSourceChip() {
        if (!sourceChip || !state.payload) {
            return;
        }

        sourceChip.textContent = `Synced ${
            state.payload.metadata.source_updated_at
                ? formatTimestamp(state.payload.metadata.source_updated_at)
                : "recently"
        }`;
    }

    function renderAll() {
        renderDaySelect();
        renderSummary();
        renderAlertsList();
        renderSourceChip();
        refreshMapImage();
    }

    async function loadAlerts() {
        try {
            const response = await fetch(config.dataUrl, {
                headers: { Accept: "application/json" },
            });
            const payload = await response.json();

            if (!response.ok) {
                throw new Error(payload.error || "Unable to fetch statewise alerts.");
            }

            state.payload = payload;
            renderAll();
        } catch (error) {
            const message = error && error.message ? error.message : String(error);
            if (summaryGrid) {
                summaryGrid.innerHTML = `<div class="alerts-empty-state">${message}</div>`;
            }
            if (alertsList) {
                alertsList.innerHTML = "";
            }
        }
    }

    if (daySelect) {
        daySelect.addEventListener("change", function (event) {
            state.selectedDay = event.target.value;
            renderSummary();
            renderAlertsList();
            refreshMapImage();
        });
    }



    loadAlerts();
})();
