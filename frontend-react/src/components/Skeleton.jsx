import React from 'react';

// Single skeleton block.
export const Skeleton = ({ h = 16, w = '100%', radius = 'var(--radius-md)', className = '', style = {} }) => (
    <div
        className={`skeleton ${className}`}
        style={{ height: h, width: w, borderRadius: radius, ...style }}
        aria-hidden="true"
    />
);

// Multi-line text skeleton.
export const SkeletonText = ({ lines = 3, gap = 8 }) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap }} aria-hidden="true">
        {Array.from({ length: lines }).map((_, i) => (
            <Skeleton key={i} h={12} w={i === lines - 1 ? '60%' : '100%'} />
        ))}
    </div>
);

// Card-shaped skeleton (icon chip + two text lines).
export const SkeletonCard = ({ height = 96 }) => (
    <div className="card" style={{ padding: '1.25rem', minHeight: height }} aria-hidden="true">
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <Skeleton h={40} w={40} radius="var(--radius-sm)" />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
                <Skeleton h={14} w="50%" />
                <Skeleton h={10} w="80%" />
            </div>
        </div>
    </div>
);

export default Skeleton;
