tsParticles.load("tsparticles", {
    background: {
        color: {
            value: "#ffffff"
        }
    },
    particles: {
        number: {
            value: 200
        },
        color: {
            value: "#014aa7"
        },
        shape: {
            type: "circle"
        },
        opacity: {
            value: 0.5
        },
        size: {
            value: 3
        },
        links: {
            enable: true,
            distance: 150,
            color: "#00446b",
            opacity: 0.4,
            width: 1
        },
        move: {
            enable: true,
            speed: 1
        }
    },
    interactivity: {
        events: {
            onhover: {
                enable: true,
                mode: "repulse"
            }
        }
    }
});
