// static/js/posture-helper.js

/**
 * Système de notification pour les conseils de posture
 */
class PostureNotifier {
    constructor() {
        this.lastNotification = null;
        this.notificationCooldown = 30000; // 30 secondes entre notifications
    }

    /**
     * Affiche une notification système si supporté
     */
    async requestPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            await Notification.requestPermission();
        }
    }

    /**
     * Envoie une notification de correction
     */
    notify(problem, tip) {
        const now = Date.now();

        // Vérifier le cooldown
        if (this.lastNotification && (now - this.lastNotification) < this.notificationCooldown) {
            return;
        }

        if ('Notification' in window && Notification.permission === 'granted') {
            const notification = new Notification('⚠️ Correction de Posture', {
                body: `${problem}: ${tip}`,
                icon: '/static/img/logo.png',
                badge: '/static/img/badge.png',
                vibrate: [200, 100, 200],
                tag: 'posture-alert'
            });

            notification.onclick = () => {
                window.focus();
                notification.close();
            };

            this.lastNotification = now;
        }
    }

    /**
     * Obtient le conseil approprié pour un problème
     */
    getTip(problem) {
        const tips = {
            'neck': {
                title: 'Tête trop penchée',
                tip: 'Rentrez votre menton et alignez votre tête avec votre colonne vertébrale.',
                exercise: 'Faites 5 Chin Tucks maintenant'
            },
            'back': {
                title: 'Dos courbé',
                tip: 'Redressez votre dos et utilisez le support lombaire de votre chaise.',
                exercise: 'Faites 5 Cat-Cow Stretches'
            },
            'shoulders': {
                title: 'Épaules déséquilibrées',
                tip: 'Détendez vos épaules et assurez-vous qu\'elles sont au même niveau.',
                exercise: 'Faites 10 Shoulder Rolls'
            }
        };

        return tips[problem] || null;
    }
}

/**
 * Gestionnaire de statistiques de session
 */
class SessionStats {
    constructor() {
        this.goodPostureTime = 0;
        this.badPostureTime = 0;
        this.neckIssues = 0;
        this.backIssues = 0;
        this.shoulderIssues = 0;
        this.lastUpdate = Date.now();
    }

    update(result) {
        const now = Date.now();
        const elapsed = (now - this.lastUpdate) / 1000;

        if (result.is_good_posture) {
            this.goodPostureTime += elapsed;
        } else {
            this.badPostureTime += elapsed;

            if (!result.neck_ok) this.neckIssues++;
            if (!result.back_ok) this.backIssues++;
            if (!result.shoulders_ok) this.shoulderIssues++;
        }

        this.lastUpdate = now;
    }

    getScore() {
        const total = this.goodPostureTime + this.badPostureTime;
        return total > 0 ? Math.round((this.goodPostureTime / total) * 100) : 100;
    }

    getMostCommonIssue() {
        const issues = {
            neck: this.neckIssues,
            back: this.backIssues,
            shoulders: this.shoulderIssues
        };

        return Object.keys(issues).reduce((a, b) =>
            issues[a] > issues[b] ? a : b
        );
    }

    getReport() {
        return {
            score: this.getScore(),
            goodTime: Math.round(this.goodPostureTime),
            badTime: Math.round(this.badPostureTime),
            totalTime: Math.round(this.goodPostureTime + this.badPostureTime),
            mostCommonIssue: this.getMostCommonIssue(),
            issues: {
                neck: this.neckIssues,
                back: this.backIssues,
                shoulders: this.shoulderIssues
            }
        };
    }
}

/**
 * Gestionnaire de sons d'alerte personnalisables
 */
class AudioAlerts {
    constructor() {
        this.audioContext = null;
        this.enabled = true;
    }

    initialize() {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
    }

    /**
     * Joue un son de correction doux
     */
    playSoftAlert() {
        if (!this.enabled) return;

        this.initialize();
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        oscillator.frequency.value = 600;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.2, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);

        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.3);
    }

    /**
     * Joue un son d'alerte urgent
     */
    playUrgentAlert() {
        if (!this.enabled) return;

        this.initialize();

        // Double beep
        for (let i = 0; i < 2; i++) {
            setTimeout(() => {
                const oscillator = this.audioContext.createOscillator();
                const gainNode = this.audioContext.createGain();

                oscillator.connect(gainNode);
                gainNode.connect(this.audioContext.destination);

                oscillator.frequency.value = 800;
                oscillator.type = 'square';

                gainNode.gain.setValueAtTime(0.15, this.audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.2);

                oscillator.start(this.audioContext.currentTime);
                oscillator.stop(this.audioContext.currentTime + 0.2);
            }, i * 300);
        }
    }

    /**
     * Joue un son de succès
     */
    playSuccessSound() {
        if (!this.enabled) return;

        this.initialize();

        const frequencies = [523.25, 659.25, 783.99]; // Do, Mi, Sol

        frequencies.forEach((freq, index) => {
            setTimeout(() => {
                const oscillator = this.audioContext.createOscillator();
                const gainNode = this.audioContext.createGain();

                oscillator.connect(gainNode);
                gainNode.connect(this.audioContext.destination);

                oscillator.frequency.value = freq;
                oscillator.type = 'sine';

                gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.2);

                oscillator.start(this.audioContext.currentTime);
                oscillator.stop(this.audioContext.currentTime + 0.2);
            }, index * 100);
        });
    }

    toggle() {
        this.enabled = !this.enabled;
        return this.enabled;
    }
}

/**
 * Gestionnaire de rappels de pause
 */
class BreakReminder {
    constructor(interval = 30) { // 30 minutes par défaut
        this.interval = interval * 60 * 1000;
        this.lastBreak = Date.now();
        this.timer = null;
        this.enabled = true;
    }

    start() {
        if (!this.enabled) return;

        this.timer = setInterval(() => {
            this.showBreakReminder();
        }, this.interval);
    }

    stop() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    showBreakReminder() {
        if (!this.enabled) return;

        const modal = document.createElement('div');
        modal.className = 'break-reminder-modal';
        modal.innerHTML = `
            <div class="break-reminder-content">
                <h3>⏰ Temps de Pause !</h3>
                <p>Vous travaillez depuis ${this.interval / 60000} minutes.</p>
                <p>Prenez une pause de 5 minutes pour :</p>
                <ul>
                    <li>🚶 Marcher un peu</li>
                    <li>🤸 Faire des étirements</li>
                    <li>👀 Reposer vos yeux</li>
                    <li>💧 Boire de l'eau</li>
                </ul>
                <button onclick="this.parentElement.parentElement.remove()">
                    J'ai compris !
                </button>
            </div>
        `;

        document.body.appendChild(modal);

        // Retirer automatiquement après 30 secondes
        setTimeout(() => {
            if (modal.parentElement) {
                modal.remove();
            }
        }, 30000);

        this.lastBreak = Date.now();
    }

    setInterval(minutes) {
        this.interval = minutes * 60 * 1000;
        if (this.timer) {
            this.stop();
            this.start();
        }
    }

    toggle() {
        this.enabled = !this.enabled;
        if (this.enabled) {
            this.start();
        } else {
            this.stop();
        }
        return this.enabled;
    }
}

/**
 * Utilitaires de formatage
 */
const PostureUtils = {
    formatTime: (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    },

    formatDuration: (seconds) => {
        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);

        if (hours > 0) {
            return `${hours}h ${mins}m`;
        } else if (mins > 0) {
            return `${mins}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    },

    getPostureGrade: (score) => {
        if (score >= 90) return { grade: 'A', color: '#10b981', text: 'Excellent' };
        if (score >= 80) return { grade: 'B', color: '#3b82f6', text: 'Très bien' };
        if (score >= 70) return { grade: 'C', color: '#f59e0b', text: 'Bien' };
        if (score >= 60) return { grade: 'D', color: '#ef4444', text: 'Passable' };
        return { grade: 'F', color: '#991b1b', text: 'À améliorer' };
    },

    vibrate: (pattern = [200]) => {
        if ('vibrate' in navigator) {
            navigator.vibrate(pattern);
        }
    }
};

// Exporter pour utilisation globale
window.PostureNotifier = PostureNotifier;
window.SessionStats = SessionStats;
window.AudioAlerts = AudioAlerts;
window.BreakReminder = BreakReminder;
window.PostureUtils = PostureUtils;