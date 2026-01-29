'use strict';

const React = require('react');
const { View, StyleSheet } = require('react-native');

const LayoutRegistryContext = React.createContext(null);

/**
 * Enregistre les layouts une seule fois (ex. à la racine). Les composants utilisent
 * layoutKey="screen" pour récupérer le layout sans importer le JSON à chaque niveau.
 *
 * @param {Object} props.layouts - Map { clé: tableau de boîtes }. Ex. { screen: [...], profile: [...] }
 *   Les valeurs peuvent être des tableaux ou le résultat de require('./layouts/xxx_layout.json').
 */
function LayoutProvider({ layouts, children }) {
  const value = React.useMemo(() => (layouts != null ? layouts : {}), [layouts]);
  return React.createElement(LayoutRegistryContext.Provider, { value }, children);
}

/**
 * Trouve une boîte dans le layout par id ou par name (utilitaire exporté).
 */
function findBox(layout, key) {
  if (layout == null || !Array.isArray(layout)) return null;
  if (key.id != null) {
    const byId = layout.find((b) => b.id === key.id);
    if (byId) return byId;
  }
  if (key.name != null && String(key.name).trim() !== '') {
    const byName = layout.find((b) => b.name != null && String(b.name).trim() === String(key.name).trim());
    if (byName) return byName;
  }
  return null;
}

/**
 * Composant qui positionne ses enfants selon un layout (JSON généré par l'outil / split-layouts).
 *
 * Props:
 *   - layout: tableau de boîtes (ex. depuis *_layout.json) ; optionnel si layoutKey est utilisé
 *   - layoutKey: clé pour récupérer le layout depuis LayoutProvider (évite d'importer le JSON ici)
 *   - style: style optionnel du conteneur
 *   - children: composants avec layoutBoxId ou layoutBoxName pour être positionnés
 *
 * Si layoutKey est fourni et qu'un LayoutProvider est au-dessus, le layout est pris dans le contexte.
 */
function LayoutView({ layout: layoutProp, layoutKey, style, children }) {
  const registry = React.useContext(LayoutRegistryContext);
  const layout = React.useMemo(() => {
    if (layoutProp != null && Array.isArray(layoutProp)) return layoutProp;
    if (layoutKey != null && registry != null && registry[layoutKey] != null) {
      const L = registry[layoutKey];
      return Array.isArray(L) ? L : L;
    }
    return null;
  }, [layoutProp, layoutKey, registry]);

  const boxMap = React.useMemo(() => {
    const map = new Map();
    if (layout == null || !Array.isArray(layout)) return map;
    layout.forEach((b) => {
      if (b.id != null) map.set(`id:${b.id}`, b);
      if (b.name != null && String(b.name).trim() !== '') map.set(`name:${String(b.name).trim()}`, b);
    });
    return map;
  }, [layout]);

  const positioned = React.Children.map(children, (child) => {
    if (child == null || typeof child !== 'object') return child;
    const props = child.props || {};
    const boxId = props.layoutBoxId;
    const boxName = props.layoutBoxName;
    if (boxId == null && (boxName == null || String(boxName).trim() === '')) return child;

    const box = boxMap.get(`id:${boxId}`) ?? boxMap.get(`name:${String(boxName).trim()}`) ?? null;
    if (box == null) return child;

    const boxStyle = {
      position: 'absolute',
      left: `${Number(box.xPct)}%`,
      top: `${Number(box.yPct)}%`,
      width: `${Number(box.wPct)}%`,
      height: `${Number(box.hPct)}%`,
    };

    return (
      <View key={box.id ?? box.name ?? String(Math.random())} style={boxStyle}>
        {child}
      </View>
    );
  });

  return <View style={[styles.container, style]}>{positioned}</View>;
}

const styles = StyleSheet.create({
  container: {
    position: 'relative',
    width: '100%',
    height: '100%',
  },
});

module.exports = LayoutView;
module.exports.LayoutProvider = LayoutProvider;
module.exports.LayoutRegistryContext = LayoutRegistryContext;
module.exports.findBox = findBox;
