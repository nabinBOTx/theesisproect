// Adaptive Difficulty and Recommendations System

class UserStats {
    constructor() {
        this.stats = null;
        this.recommendations = null;
    }

    async loadStats() {
        try {
            const response = await fetch('/api/user-stats');
            this.stats = await response.json();
            return this.stats;
        } catch (error) {
            console.error('Error loading stats:', error);
            return null;
        }
    }

    async loadRecommendations() {
        try {
            const response = await fetch('/api/recommendations');
            const data = await response.json();
            this.recommendations = data.recommendations || [];
            return this.recommendations;
        } catch (error) {
            console.error('Error loading recommendations:', error);
            return [];
        }
    }

    async getNextDifficulty() {
        try {
            const response = await fetch('/api/next-difficulty');
            return await response.json();
        } catch (error) {
            console.error('Error getting next difficulty:', error);
            return null;
        }
    }

    displayStats() {
        if (!this.stats) return;

        const statsHtml = this.buildStatsHTML();
        const container = document.getElementById('user-stats-container');
        if (container) {
            container.innerHTML = statsHtml;
        }
    }

    displayRecommendations() {
        if (!this.recommendations || this.recommendations.length === 0) return;

        const recsHtml = this.buildRecommendationsHTML();
        const container = document.getElementById('recommendations-container');
        if (container) {
            container.innerHTML = recsHtml;
        }
    }

    buildStatsHTML() {
        const stats = this.stats;
        
        let html = `
            <div class="stats-panel">
                <h3>📊 Your Performance</h3>
                <div class="stats-overview">
                    <div class="stat-item">
                        <span class="stat-label">Overall Score:</span>
                        <span class="stat-value">${stats.overall_score}/${stats.overall_total}</span>
                        <span class="stat-percentage">${stats.overall_total > 0 ? Math.round((stats.overall_score / stats.overall_total) * 100) : 0}%</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Games Played:</span>
                        <span class="stat-value">${stats.total_games_played}</span>
                    </div>
                </div>
        `;

        if (Object.keys(stats.game_scores).length > 0) {
            html += `<div class="game-scores">`;
            for (const [game, scores] of Object.entries(stats.game_scores)) {
                const barWidth = scores.percentage;
                const barColor = scores.percentage < 50 ? '#e74c3c' : scores.percentage < 75 ? '#f39c12' : '#27ae60';
                html += `
                    <div class="game-score-item">
                        <div class="game-name">${game}</div>
                        <div class="score-bar-container">
                            <div class="score-bar" style="width: ${barWidth}%; background-color: ${barColor};"></div>
                        </div>
                        <div class="score-text">${scores.score}/${scores.total} (${scores.percentage}%)</div>
                    </div>
                `;
            }
            html += `</div>`;
        }

        html += `</div>`;
        return html;
    }

    buildRecommendationsHTML() {
        if (!this.recommendations || this.recommendations.length === 0) {
            return '<p class="no-recommendations">Great job! You\'re performing well across all games.</p>';
        }

        let html = `<div class="recommendations-panel">
            <h3>🎯 Personalized Recommendations</h3>
            <div class="recommendations-list">`;

        for (const rec of this.recommendations) {
            const priorityIcon = rec.priority === 'high' ? '🔴' : '🟡';
            const priorityLabel = rec.priority === 'high' ? 'High Priority' : 'Medium Priority';

            html += `
                <div class="recommendation-item priority-${rec.priority}">
                    <div class="rec-header">
                        <span class="priority-icon">${priorityIcon}</span>
                        <span class="rec-game">${rec.game}</span>
                        <span class="priority-label">${priorityLabel}</span>
                    </div>
                    <p class="rec-message">${rec.message}</p>
                    <div class="suggested-modules">
                        <strong>Try these modules:</strong>
                        <ul>
                            ${rec.modules.map(m => `<li>📚 ${m}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }

        html += `</div></div>`;
        return html;
    }

    displayDifficultyIndicator() {
        this.getNextDifficulty().then(data => {
            if (!data) return;

            const difficultyColors = {
                'easy': { color: '#27ae60', label: 'Easy', emoji: '🟢' },
                'medium': { color: '#f39c12', label: 'Medium', emoji: '🟡' },
                'hard': { color: '#e74c3c', label: 'Hard', emoji: '🔴' }
            };

            const diff = difficultyColors[data.difficulty] || difficultyColors['medium'];
            
            const html = `
                <div class="difficulty-indicator" style="border-left: 4px solid ${diff.color};">
                    <span class="difficulty-emoji">${diff.emoji}</span>
                    <span class="difficulty-text">Next Game Difficulty: <strong>${diff.label}</strong></span>
                    <span class="difficulty-reason">Based on ${data.percentage}% accuracy</span>
                </div>
            `;

            const container = document.getElementById('difficulty-indicator-container');
            if (container) {
                container.innerHTML = html;
            }
        });
    }
}

// Initialize stats system when page loads
document.addEventListener('DOMContentLoaded', async () => {
    const userStats = new UserStats();
    
    // Load and display stats if on a page with containers
    if (document.getElementById('user-stats-container') || 
        document.getElementById('recommendations-container')) {
        
        await userStats.loadStats();
        userStats.displayStats();
        
        await userStats.loadRecommendations();
        userStats.displayRecommendations();
    }

    // Display difficulty indicator if on game page
    if (document.getElementById('difficulty-indicator-container')) {
        userStats.displayDifficultyIndicator();
    }

    // Make stats available globally for manual access
    window.userStats = userStats;
});
