// Helper: returns true if text is predominantly English (ASCII printable)
function isEnglish(text) {
    // Allow ASCII printable characters only (no Malayalam, Hindi, etc.)
    return /^[\x00-\x7F\u2018\u2019\u201C\u201D\u2013\u2014\u2026\u00A0-\u00FF]*$/.test(text);
}

// Helper: returns true if a pubDate string is today (IST)
function isToday(pubDateStr) {
    if (!pubDateStr) return false;
    const articleDate = new Date(pubDateStr);
    const now = new Date();
    return (
        articleDate.getFullYear() === now.getFullYear() &&
        articleDate.getMonth()    === now.getMonth()    &&
        articleDate.getDate()     === now.getDate()
    );
}

function news_display(news_url, newstype) {
    fetch(news_url)
        .then(response => {
            if (response.ok) return response.json();
            throw new Error('Network response was not ok.');
        })
        .then(data => {
            
            const total = data.headlines.length;

            if (newstype === "cardtype_news") {
                const cardContainer = document.getElementById('newscard');
                let shown = 0;
                for (let index = 0; index < total; index++) {
                    const headline = data.headlines[index].headline;
                    const link     = data.news_links[index].news_link;
                    const source   = data.sources  ? data.sources[index].source   : '';
                    const pubDate  = data.pubDates ? data.pubDates[index].pubDate : '';

                    // Filter: English only
                    if (!isEnglish(headline)) continue;
                    // Filter: today's news only
                    if (!isToday(pubDate)) continue;

                    shown++;
                    const card = document.createElement('div');
                    card.className = 'col';
                    card.innerHTML = `
                        <a href="${link}" target="_blank">
                            <div class="card h-100">
                                <div class="card-body">
                                    <h5 class="card-title">${headline}</h5>
                                </div>
                                <div class="card-footer d-flex justify-content-between align-items-center">
                                    <small>${source}</small>
                                    <small>${pubDate ? new Date(pubDate).toLocaleDateString('en-IN', {day:'numeric',month:'short'}) : ''}</small>
                                </div>
                            </div>
                        </a>
                    `;
                    cardContainer.append(card);
                }
                if (shown === 0) {
                    cardContainer.innerHTML = '<p class="text-muted p-3">No English news available for today yet. Please check back later.</p>';
                }

            } else {
                const ul = document.querySelector(".ul");
                let shown = 0;
                for (let index = 0; index < total; index++) {
                    const headline = data.headlines[index].headline;
                    const link     = data.news_links[index].news_link;
                    const source   = data.sources  ? data.sources[index].source   : '';
                    const pubDate  = data.pubDates ? data.pubDates[index].pubDate : '';

                    // Filter: English only
                    if (!isEnglish(headline)) continue;
                    // Filter: today's news only
                    if (!isToday(pubDate)) continue;

                    shown++;
                    const list = document.createElement('li');
                    list.innerHTML = `
                        <div class="date">
                            <h3><small style="font-size:0.6em;">${source}</small></h3>
                            <span style="font-size:0.7em;">${pubDate ? pubDate.slice(0, 16) : ''}</span>
                        </div>
                        <a href="${link}" target="_blank">
                            <p>${headline}</p>
                        </a>
                    `;
                    ul.append(list);
                }
                if (shown === 0) {
                    ul.innerHTML = '<li class="text-muted">No English news available for today yet. Please check back later.</li>';
                }
            }
        })
        .catch(error => console.error('Error fetching data:', error));
}

const get_id = document.querySelector("h1");
if (get_id) {
    if (get_id.id === "global") {
        news_display("/news/newsglobal/", "cardtype_news");
    } else if (get_id.id === "national") {
        news_display("/news/newsnational/", "cardtype_news");
    } else if (get_id.id === "state") {
        const stateName = get_id.getAttribute("data-state");
        news_display(`/news/newsstate/${stateName}/`, "cardtype_news");
    }
}
