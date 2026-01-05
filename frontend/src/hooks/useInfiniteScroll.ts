"use client"

import { useState, useEffect, useCallback, useRef } from 'react';

interface UseInfiniteScrollOptions<T> {
    fetchMore: (page: number) => Promise<T[]>;
    pageSize?: number;
}

export function useInfiniteScroll<T>({ fetchMore, pageSize = 20 }: UseInfiniteScrollOptions<T>) {
    const [items, setItems] = useState<T[]>([]);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const observerRef = useRef<IntersectionObserver | null>(null);

    const loadMore = useCallback(async () => {
        if (loading || !hasMore) return;

        setLoading(true);
        try {
            const newItems = await fetchMore(page);
            if (newItems.length < pageSize) {
                setHasMore(false);
            }
            setItems(prev => [...prev, ...newItems]);
            setPage(prev => prev + 1);
        } catch (error) {
            console.error('Error loading more items:', error);
        } finally {
            setLoading(false);
        }
    }, [page, loading, hasMore, fetchMore, pageSize]);

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

    useEffect(() => {
        loadMore();
    }, []); // Load initial items

    return { items, loading, hasMore, lastElementRef };
}
