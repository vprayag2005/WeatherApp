window.onload = function () {
    fetch('/news/newskerala/')
    .then(response => {
        if (response.ok) return response.json();
        throw new Error('Network response was not ok.');
    })
    .then(data => {
        
        const cardContainer = document.getElementById('newscard');
        const total = data.headlines.length;
        for (let index = 0; index < total; index++) {
            const headline = data.headlines[index].headline;
            const link     = data.news_links[index].news_link;
            const source   = data.sources ? data.sources[index].source : '';
            const pubDate  = data.pubDates ? data.pubDates[index].pubDate : '';
            const card = document.createElement('div');
            card.className = 'col';
            card.innerHTML = `
                <a href="${link}" target="_blank" style="text-decoration:none;">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">${headline}</h5>
                        </div>
                        <div class="card-footer d-flex justify-content-between align-items-center">
                            <small class="text-muted">${source}</small>
                            <small class="text-muted">${pubDate}</small>
                        </div>
                    </div>
                </a>
            `;
            cardContainer.append(card);
        }
    })
    .catch(error => console.error('Error fetching data:', error));
};
