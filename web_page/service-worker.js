self.addEventListener('install', function (event) {
    event.waitUntil(
        caches.open('v1').then(function (cache) {
            return cache.addAll([
                '/Desktop_Gadget/index.html',
                '/Desktop_Gadget/web_page/style.css',
                '/Desktop_Gadget/web_page/img/img.png',
                '/Desktop_Gadget/web_page/particles-config.js'
            ]);
        })
    );
});

self.addEventListener('fetch', function (event) {
    event.respondWith(
        caches.match(event.request).then(function (response) {
            return response || fetch(event.request);
        })
    );
});