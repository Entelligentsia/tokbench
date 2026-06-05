'use strict';

/**
 * paths.cjs — Shared path-computation helpers for Forge tools.
 *
 * Single source of truth for directory-name conventions that must be
 * consistent across substitute-placeholders.cjs, check-structure.cjs, etc.
 *
 * Exported API:
 *   getCommandsSubdir(prefix) — returns prefix.toLowerCase()
 */

/**
 * Compute the commands subdirectory name from a project prefix.
 *
 * The canonical commands subfolder under .claude/commands/ is derived
 * from the project prefix (lowercased), NOT hardcoded as 'forge'.
 *
 * @param {string} prefix — project prefix (e.g. 'ACME', 'FORGE')
 * @returns {string} lowercased prefix (e.g. 'acme', 'forge')
 */
function getCommandsSubdir(prefix) {
  if (typeof prefix !== 'string' || prefix.length === 0) {
    throw new Error('paths.getCommandsSubdir: prefix must be a non-empty string');
  }
  return prefix.toLowerCase();
}

module.exports = { getCommandsSubdir };