# CI/CD Caching Strategy Documentation

## Overview
This document explains the caching strategies implemented to optimize build times in the CI pipeline.

## Implemented Caching Layers

### 1. Dependency Caching

#### Poetry Dependencies (Python)
```yaml
- name: Cache Poetry dependencies
  uses: actions/cache@v3
  with:
    path: |
      ~/.cache/pypoetry
      ${{ matrix.path }}/.venv
      ${{ matrix.path }}/poetry.lock
    key: poetry-${{ matrix.service }}-${{ hashFiles(format('{0}/poetry.lock', matrix.path)) }}
```

**Benefits:**
- Caches downloaded Python packages
- Preserves virtual environments
- Speeds up `poetry install` from minutes to seconds

#### Node.js Dependencies
```yaml
- name: Cache Node.js dependencies
  uses: actions/cache@v3
  with:
    path: |
      ~/.npm
      ${{ matrix.path }}/node_modules
    key: node-${{ matrix.service }}-${{ hashFiles(format('{0}/package-lock.json', matrix.path)) }}
```

**Benefits:**
- Caches npm packages
- Reduces `npm install` time significantly
- Works for both frontend and user services

#### Go Modules
```yaml
- name: Cache Go modules
  uses: actions/cache@v3
  with:
    path: |
      ~/go/pkg/mod
      ${{ matrix.path }}/go.sum
    key: go-${{ matrix.service }}-${{ hashFiles(format('{0}/go.sum', matrix.path)) }}
```

**Benefits:**
- Caches Go module downloads
- Speeds up dependency resolution
- Preserves build cache

#### Rust Cargo
```yaml
- name: Cache Rust build artifacts
  uses: actions/cache@v3
  with:
    path: |
      ~/.cargo/registry
      ~/.cargo/git
      ${{ matrix.path }}/target
    key: rust-${{ matrix.service }}-${{ hashFiles(format('{0}/Cargo.lock', matrix.path)) }}
```

**Benefits:**
- Caches downloaded crates
- Preserves compiled dependencies (most impactful for Rust)
- Can reduce Rust builds from 30+ minutes to under 2 minutes

### 2. Docker Layer Caching

```yaml
- name: Cache Docker layers
  uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: docker-${{ matrix.service }}-${{ github.sha }}
```

**Configuration in docker/build-push-action:**
```yaml
cache-from: type=local,src=/tmp/.buildx-cache
cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max
```

**Benefits:**
- Caches intermediate Docker build layers
- Dramatically speeds up subsequent builds
- Particularly effective with multi-stage builds

## Cache Keys Strategy

Each cache uses a specific key format:
- `language-service-hash(dependency_file)`
- Examples: `poetry-chat-abc123`, `node-frontend-def456`

This ensures:
- Cache invalidation when dependencies change
- Service isolation (caches don't interfere with each other)
- Build reproducibility

## Expected Performance Improvements

| Service | Without Cache | With Cache | Improvement |
|---------|---------------|------------|-------------|
| Gateway (Rust) | 30+ minutes | 1-2 minutes | 95%+ faster |
| Chat (Python) | 2-3 minutes | 30-60 seconds | 75%+ faster |
| Frontend/User (Node.js) | 1-2 minutes | 20-40 seconds | 75%+ faster |
| Message (Go) | 1-2 minutes | 30-60 seconds | 75%+ faster |

## Monitoring Cache Effectiveness

### Checking Cache Hits/Misses
Add this step to debug cache performance:

```yaml
- name: Debug cache status
  run: |
    echo "Cache hit: ${{ steps.cache-node.outputs.cache-hit }}"
    echo "Cache key: ${{ steps.cache-node.outputs.cache-primary-key }}"
```

### Cache Size Monitoring
```yaml
- name: Check cache sizes
  run: |
    du -sh ~/.cache/pypoetry 2>/dev/null || echo "Poetry cache not found"
    du -sh ~/.npm 2>/dev/null || echo "NPM cache not found"
    du -sh ~/.cargo/registry 2>/dev/null || echo "Cargo cache not found"
```

## Troubleshooting

### Cache Corruption
If builds start failing mysteriously:
1. Clear the cache by changing the cache key prefix
2. Example: Change `poetry-` to `poetry-v2-`

### Cache Too Large
Monitor cache sizes and consider:
- Using `actions/cache/save` with compression
- Implementing cache cleanup policies
- Splitting large caches into smaller ones

### Platform-Specific Issues
For multi-platform builds:
```yaml
key: docker-${{ matrix.service }}-${{ github.sha }}-${{ runner.os }}
```

## Best Practices

1. **Always use restore-keys**: Provides fallback cache when exact key misses
2. **Hash dependency files**: Ensures cache invalidation when deps change
3. **Separate caches by service**: Prevents interference between services
4. **Monitor regularly**: Check cache hit rates and sizes
5. **Update documentation**: Keep this file updated with changes

## Future Enhancements

Consider adding:
- Cache warming jobs for predictable dependency updates
- Cache size limits and cleanup policies
- Cross-run cache sharing for related builds
- Metrics collection for cache performance tracking

## References

- [GitHub Actions Cache](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [Docker Buildx Caching](https://docs.docker.com/build/cache/)
- [Language-specific caching guides](https://github.com/actions/cache)