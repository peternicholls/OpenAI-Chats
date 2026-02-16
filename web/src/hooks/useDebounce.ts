import { useState, useEffect } from "react";

/**
 * Custom hook that debounces a value by the specified delay.
 * Returns the debounced value that only updates after the delay has passed
 * without the input value changing.
 */
export function useDebounce<T>(value: T, delay: number = 500): T {
    const [debouncedValue, setDebouncedValue] = useState<T>(value);

    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedValue(value);
        }, delay);

        return () => {
            clearTimeout(timer);
        };
    }, [value, delay]);

    return debouncedValue;
}
