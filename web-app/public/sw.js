// Service Worker for Push Notifications
const CACHE_NAME = 'jquants-stock-prediction-v1';
const urlsToCache = [
  '/',
  '/today',
  '/reports',
  '/settings',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/favicon.ico'
];

// インストール時の処理
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Cache opened');
        return cache.addAll(urlsToCache);
      })
  );
});

// フェッチ時の処理
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // キャッシュがある場合はそれを返す
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});

// プッシュ通知の受信処理
self.addEventListener('push', (event) => {
  console.log('Push message received:', event);
  
  const options = {
    body: '新しい株価分析結果が利用可能です',
    icon: '/favicon.ico',
    badge: '/favicon.ico',
    tag: 'stock-analysis',
    data: {
      url: '/today'
    },
    actions: [
      {
        action: 'view',
        title: '詳細を見る',
        icon: '/favicon.ico'
      },
      {
        action: 'dismiss',
        title: '閉じる'
      }
    ]
  };

  if (event.data) {
    const data = event.data.json();
    options.body = data.message || options.body;
    options.data = data.data || options.data;
  }

  event.waitUntil(
    self.registration.showNotification('J-Quants株価予測', options)
  );
});

// 通知クリック時の処理
self.addEventListener('notificationclick', (event) => {
  console.log('Notification clicked:', event);
  
  event.notification.close();

  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow(event.notification.data?.url || '/today')
    );
  } else if (event.action === 'dismiss') {
    // 何もしない
  } else {
    // デフォルトの動作
    event.waitUntil(
      clients.openWindow('/today')
    );
  }
});

// バックグラウンド同期
// GitHub Pages 等の静的ホスティングでは /api は存在しないため無効化
const isStaticHosting = (() => {
  try {
    return /github\.io$/i.test(self.location.hostname);
  } catch (_) {
    return false;
  }
})();

self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    if (isStaticHosting) {
      // 静的ホスティングでは何もしない
      return;
    }
    event.waitUntil(
      fetch('/api/background-sync')
        .then((response) => {
          if (response.ok) {
            console.log('Background sync completed');
          }
        })
        .catch((error) => {
          console.error('Background sync failed:', error);
        })
    );
  }
});

// メッセージの受信処理
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
