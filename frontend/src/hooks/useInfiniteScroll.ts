"use client"

import { useState, useEffect, useCallback, useRef } from 'react';

interface UseInfiniteScrollOptions<T> {
    fetchMore: (page: number) => Promise<T[]>;
    pageSize?: number;
    dependencies?: any[];
}

export function useInfiniteScroll<T>({ fetchMore, pageSize = 20, dependencies = [] }: UseInfiniteScrollOptions<T>) {
    const [items, setItems] = useState<T[]>([]);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const observerRef = useRef<IntersectionObserver | null>(null);

    const loadMore = useCallback(async (reset = false) => {
        if (loading || (!hasMore && !reset)) return;

        // Prevent race conditions or overlapping calls if needed
        // but for now simple loading check is ok

        setLoading(true);
        try {
            const currentPage = reset ? 0 : page;
            const newItems = await fetchMore(currentPage);

            if (newItems.length < pageSize) {
                setHasMore(false);
            } else {
                setHasMore(true);
            }

            if (reset) {
                setItems(newItems);
                setPage(1);
            } else {
                setItems(prev => [...prev, ...newItems]);
                setPage(prev => prev + 1);
            }
        } catch (error) {
            console.error('Error loading more items:', error);
            if (reset) setItems([]);
        } finally {
            setLoading(false);
        }
    }, [page, loading, hasMore, fetchMore, pageSize]);

    // Handle reset when dependencies change
    useEffect(() => {
        // Reset state
        setPage(0);
        setHasMore(true);
        setItems([]);

        // Trigger generic load with reset logic
        // We use a small timeout to let state flush or just call logic directly
        // Better: logic inside loadMore handling reset flag
        loadMore(true);
    }, dependencies); // eslint-disable-line react-hooks/exhaustive-deps

    const lastElementRef = useCallback((node: HTMLElement | null) => {
        if (loading) return;
        if (observerRef.current) observerRef.current.disconnect();

        observerRef.current = new IntersectionObserver(entries => {
            if (entries[0].isIntersecting && hasMore) {
                loadMore();
            }
        });

        if (node) observerRef.current.observe(node);
    }, [loading, hasMore, loadMore]);

    return { items, loading, hasMore, lastElementRef };
}
