function renderTeamChart(data) {
    const ctx = document.getElementById('teamChart').getContext('2d');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.teams, // Team Names
            datasets: [{
                label: 'Total Points',
                data: data.points, // Team Points
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}