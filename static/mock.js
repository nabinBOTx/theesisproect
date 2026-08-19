// Comprehensive mock data for CYBER//GUARD gamified cybersecurity site
window.MOCK = {
  users: [
    {
      id: 'u1',
      username: 'h4ck3rpro',
      displayName: 'H4ck3rPro',
      email: 'hacker@cyber.guard',
      avatar: null,
      badges: ['starter', 'phisher', 'password_master', 'social_ace', 'network_pro', 'speed_demon', 'perfect_score', 'level_10'],
      progress: {
        phish_hunter: 100,
        password_defense: 95,
        social_engineering: 88,
        network_challenge: 92,
        choose_2fa: 85,
        safe_to_click: 90,
        inbox: 93
      },
      totalXP: 15420,
      level: 12,
      joinedDate: '2024-01-15T10:30:00Z',
      sessions: [
        { gameId: 'phish_hunter', score: 100, date: '2024-03-10T14:20:00Z' },
        { gameId: 'password_defense', score: 95, date: '2024-03-09T16:45:00Z' },
        { gameId: 'network_challenge', score: 100, date: '2024-03-08T11:30:00Z' }
      ]
    },
    {
      id: 'u2',
      username: 'securekid',
      displayName: 'SecureKid',
      email: 'secure@cyber.guard',
      avatar: null,
      badges: ['starter', 'phisher', 'password_master', 'level_5', 'consistent'],
      progress: {
        phish_hunter: 92,
        password_defense: 88,
        social_engineering: 75,
        network_challenge: 80,
        choose_2fa: 70,
        safe_to_click: 85,
        inbox: 78
      },
      totalXP: 14890,
      level: 11,
      joinedDate: '2024-01-20T09:15:00Z',
      sessions: [
        { gameId: 'phish_hunter', score: 92, date: '2024-03-10T10:15:00Z' },
        { gameId: 'password_defense', score: 88, date: '2024-03-09T14:30:00Z' }
      ]
    },
    {
      id: 'u3',
      username: 'ciphermaster',
      displayName: 'CipherMaster',
      email: 'cipher@cyber.guard',
      avatar: null,
      badges: ['starter', 'phisher', 'password_master', 'network_pro', 'level_8'],
      progress: {
        phish_hunter: 85,
        password_defense: 90,
        social_engineering: 70,
        network_challenge: 95,
        choose_2fa: 75,
        safe_to_click: 80,
        inbox: 82
      },
      totalXP: 13560,
      level: 11,
      joinedDate: '2024-02-01T13:45:00Z',
      sessions: [
        { gameId: 'network_challenge', score: 95, date: '2024-03-09T09:20:00Z' },
        { gameId: 'password_defense', score: 90, date: '2024-03-08T15:10:00Z' }
      ]
    },
    {
      id: 'u4',
      username: 'netsecninja',
      displayName: 'NetSecNinja',
      email: 'ninja@cyber.guard',
      avatar: null,
      badges: ['starter', 'network_pro', 'level_5'],
      progress: {
        phish_hunter: 65,
        password_defense: 70,
        social_engineering: 60,
        network_challenge: 95,
        choose_2fa: 55,
        safe_to_click: 68,
        inbox: 62
      },
      totalXP: 12340,
      level: 10,
      joinedDate: '2024-02-10T11:00:00Z',
      sessions: [
        { gameId: 'network_challenge', score: 95, date: '2024-03-09T12:00:00Z' }
      ]
    },
    {
      id: 'u5',
      username: 'byteguard',
      displayName: 'ByteGuard',
      email: 'byte@cyber.guard',
      avatar: null,
      badges: ['starter', 'level_3'],
      progress: {
        phish_hunter: 55,
        password_defense: 60,
        social_engineering: 45,
        network_challenge: 50,
        choose_2fa: 40,
        safe_to_click: 58,
        inbox: 52
      },
      totalXP: 11890,
      level: 10,
      joinedDate: '2024-02-15T08:30:00Z',
      sessions: []
    },
    {
      id: 'u6',
      username: 'authmaster',
      displayName: 'AuthMaster',
      email: 'auth@cyber.guard',
      avatar: null,
      badges: ['starter', 'phisher', 'level_4'],
      progress: {
        phish_hunter: 75,
        password_defense: 68,
        social_engineering: 55,
        network_challenge: 62,
        choose_2fa: 85,
        safe_to_click: 70,
        inbox: 73
      },
      totalXP: 10560,
      level: 9,
      joinedDate: '2024-02-20T14:20:00Z',
      sessions: []
    },
    {
      id: 'u7',
      username: 'firewallpro',
      displayName: 'FirewallPro',
      email: 'firewall@cyber.guard',
      avatar: null,
      badges: ['starter', 'network_pro'],
      progress: {
        phish_hunter: 58,
        password_defense: 62,
        social_engineering: 50,
        network_challenge: 88,
        choose_2fa: 55,
        safe_to_click: 60,
        inbox: 57
      },
      totalXP: 9780,
      level: 9,
      joinedDate: '2024-02-25T10:45:00Z',
      sessions: []
    }
  ],

  games: [
    {
      id: 'phish_hunter',
      title: 'Phish Hunter',
      desc: 'Identify phishing emails and malicious links. Spot the red flags and protect yourself from scams.',
      difficulty: 'Easy',
      category: 'Phishing',
      xpPerQuestion: 50,
      totalQuestions: 8
    },
    {
      id: 'password_defense',
      title: 'Password Cracker Defense',
      desc: 'Test password strength and learn secure practices. Master the art of creating uncrackable passwords.',
      difficulty: 'Medium',
      category: 'Passwords',
      xpPerQuestion: 75,
      totalQuestions: 8
    },
    {
      id: 'social_engineering',
      title: 'Social Engineering Scenarios',
      desc: 'Interactive decision-making challenges. Make the right choices under pressure and learn to recognize manipulation.',
      difficulty: 'Medium',
      category: 'Social Engineering',
      xpPerQuestion: 100,
      totalQuestions: 8
    },
    {
      id: 'network_challenge',
      title: 'Network Security Challenge',
      desc: 'Learn basic network security concepts. Understand how to protect data in transit and secure connections.',
      difficulty: 'Hard',
      category: 'Networking',
      xpPerQuestion: 125,
      totalQuestions: 6
    },
    {
      id: 'choose_2fa',
      title: 'Choose 2FA',
      desc: 'Select the best two-factor authentication method for different scenarios. Enhance your account security.',
      difficulty: 'Medium',
      category: 'Authentication',
      xpPerQuestion: 80,
      totalQuestions: 4
    },
    {
      id: 'safe_to_click',
      title: 'Safe to Click',
      desc: 'Quickly identify which links are safe to click and which are dangerous. Perfect for daily practice.',
      difficulty: 'Easy',
      category: 'Web Security',
      xpPerQuestion: 45,
      totalQuestions: 6
    },
    {
      id: 'inbox',
      title: 'Inbox Investigator',
      desc: 'Analyze emails and identify phishing attempts. Become an expert at spotting malicious messages.',
      difficulty: 'Medium',
      category: 'Email Security',
      xpPerQuestion: 90,
      totalQuestions: 5
    }
  ],

  achievements: [
    {
      id: 'starter',
      name: 'Initiate',
      desc: 'Create your first account and join the security force',
      icon: '⭐',
      requirement: 'signup',
      xpReward: 100
    },
    {
      id: 'phisher',
      name: 'Phish Hunter',
      desc: 'Score 80% or higher in Phish Hunter game',
      icon: '🎣',
      requirement: 'game_score',
      gameId: 'phish_hunter',
      threshold: 80,
      xpReward: 250
    },
    {
      id: 'password_master',
      name: 'Password Master',
      desc: 'Achieve 90% or higher in Password Defense',
      icon: '🗝️',
      requirement: 'game_score',
      gameId: 'password_defense',
      threshold: 90,
      xpReward: 300
    },
    {
      id: 'social_ace',
      name: 'Social Ace',
      desc: 'Master Social Engineering scenarios with 85%+ score',
      icon: '🎭',
      requirement: 'game_score',
      gameId: 'social_engineering',
      threshold: 85,
      xpReward: 400
    },
    {
      id: 'network_pro',
      name: 'Network Pro',
      desc: 'Excel in Network Security Challenge (90%+)',
      icon: '🌐',
      requirement: 'game_score',
      gameId: 'network_challenge',
      threshold: 90,
      xpReward: 500
    },
    {
      id: 'speed_demon',
      name: 'Speed Demon',
      desc: 'Complete any game in under 2 minutes',
      icon: '⚡',
      requirement: 'completion_time',
      threshold: 120,
      xpReward: 200
    },
    {
      id: 'perfect_score',
      name: 'Perfect Score',
      desc: 'Achieve 100% on any game',
      icon: '💯',
      requirement: 'perfect_score',
      xpReward: 500
    },
    {
      id: 'level_3',
      name: 'Rising Star',
      desc: 'Reach level 3',
      icon: '🌟',
      requirement: 'level',
      threshold: 3,
      xpReward: 150
    },
    {
      id: 'level_5',
      name: 'Security Specialist',
      desc: 'Reach level 5',
      icon: '🏆',
      requirement: 'level',
      threshold: 5,
      xpReward: 300
    },
    {
      id: 'level_8',
      name: 'Cyber Warrior',
      desc: 'Reach level 8',
      icon: '⚔️',
      requirement: 'level',
      threshold: 8,
      xpReward: 500
    },
    {
      id: 'level_10',
      name: 'Master Defender',
      desc: 'Reach level 10',
      icon: '👑',
      requirement: 'level',
      threshold: 10,
      xpReward: 750
    },
    {
      id: 'consistent',
      name: 'Consistent',
      desc: 'Play games for 7 days in a row',
      icon: '📅',
      requirement: 'daily_streak',
      threshold: 7,
      xpReward: 350
    },
    {
      id: 'first_blood',
      name: 'First Blood',
      desc: 'Complete your first game',
      icon: '🎯',
      requirement: 'first_completion',
      xpReward: 100
    },
    {
      id: 'diligent',
      name: 'Diligent',
      desc: 'Complete 10 games total',
      icon: '📚',
      requirement: 'total_completions',
      threshold: 10,
      xpReward: 400
    }
  ],

  leaderboard: [
    { username: 'h4ck3rpro', score: 15420, level: 12 },
    { username: 'securekid', score: 14890, level: 11 },
    { username: 'ciphermaster', score: 13560, level: 11 },
    { username: 'netsecninja', score: 12340, level: 10 },
    { username: 'byteguard', score: 11890, level: 10 },
    { username: 'authmaster', score: 10560, level: 9 },
    { username: 'firewallpro', score: 9780, level: 9 }
  ],

  sessions: [],

  // Helper functions
  getUserByUsername: function(username) {
    return this.users.find(u => u.username.toLowerCase() === username.toLowerCase());
  },

  getUserById: function(id) {
    return this.users.find(u => u.id === id);
  },

  getGameById: function(gameId) {
    return this.games.find(g => g.id === gameId);
  },

  getAchievementById: function(achievementId) {
    return this.achievements.find(a => a.id === achievementId);
  },

  calculateXPForScore: function(gameId, score, total) {
    const game = this.getGameById(gameId);
    if (!game) return 0;
    
    const percentage = (score / total) * 100;
    const baseXP = game.xpPerQuestion * game.totalQuestions;
    return Math.floor(baseXP * (percentage / 100));
  },

  calculateLevel: function(totalXP) {
    // Level formula: level = sqrt(xp / 100)
    return Math.floor(Math.sqrt(totalXP / 100)) + 1;
  },

  checkAchievements: function(userId, gameId, score, total, timeTaken) {
    const user = this.getUserById(userId);
    if (!user) return [];

    const unlocked = [];
    const percentage = (score / total) * 100;

    // Check game-specific achievements
    this.achievements.forEach(achievement => {
      if (user.badges.includes(achievement.id)) return; // Already earned

      if (achievement.requirement === 'game_score' && achievement.gameId === gameId) {
        if (percentage >= achievement.threshold) {
          user.badges.push(achievement.id);
          user.totalXP = (user.totalXP || 0) + achievement.xpReward;
          unlocked.push(achievement);
        }
      } else if (achievement.requirement === 'perfect_score' && percentage === 100) {
        user.badges.push(achievement.id);
        user.totalXP = (user.totalXP || 0) + achievement.xpReward;
        unlocked.push(achievement);
      } else if (achievement.requirement === 'completion_time' && timeTaken && timeTaken <= achievement.threshold) {
        user.badges.push(achievement.id);
        user.totalXP = (user.totalXP || 0) + achievement.xpReward;
        unlocked.push(achievement);
      } else if (achievement.requirement === 'first_completion') {
        const hasCompleted = Object.values(user.progress || {}).some(p => p > 0);
        if (hasCompleted && !user.badges.includes(achievement.id)) {
          user.badges.push(achievement.id);
          user.totalXP = (user.totalXP || 0) + achievement.xpReward;
          unlocked.push(achievement);
        }
      }
    });

    // Update level
    user.level = this.calculateLevel(user.totalXP);

    // Check level-based achievements
    this.achievements.forEach(achievement => {
      if (achievement.requirement === 'level' && !user.badges.includes(achievement.id)) {
        if (user.level >= achievement.threshold) {
          user.badges.push(achievement.id);
          user.totalXP = (user.totalXP || 0) + achievement.xpReward;
          unlocked.push(achievement);
        }
      }
    });

    return unlocked;
  }
};
