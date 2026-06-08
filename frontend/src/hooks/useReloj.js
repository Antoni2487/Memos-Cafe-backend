import { useState, useEffect } from "react";

export function useReloj() {
    const [ahora, setAhora] = useState(new Date());

    useEffect(() => {
        const intervalo = setInterval(() => {
            console.log("useReloj tick", new Date().toLocaleTimeString());
            setAhora(new Date());
        }, 1000);

        const handleVisibility = () => {
            if (document.visibilityState === "visible") {
                setAhora(new Date());
            }
        };

        document.addEventListener("visibilitychange", handleVisibility);

        return () => {
            clearInterval(intervalo);
            document.removeEventListener("visibilitychange", handleVisibility);
        };
    }, []);

    return ahora;
}