var __create = Object.create;
var __getProtoOf = Object.getPrototypeOf;
var __defProp = Object.defineProperty;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
function __accessProp(key) {
  return this[key];
}
var __toESMCache_node;
var __toESMCache_esm;
var __toESM = (mod, isNodeMode, target) => {
  var canCache = mod != null && typeof mod === "object";
  if (canCache) {
    var cache = isNodeMode ? __toESMCache_node ??= new WeakMap : __toESMCache_esm ??= new WeakMap;
    var cached = cache.get(mod);
    if (cached)
      return cached;
  }
  target = mod != null ? __create(__getProtoOf(mod)) : {};
  const to = isNodeMode || !mod || !mod.__esModule || !__hasOwnProp.call(mod, "default") ? __defProp(target, "default", { value: mod, enumerable: true }) : target;
  if (mod && typeof mod === "object" || typeof mod === "function") {
    for (let key of __getOwnPropNames(mod))
      if (!__hasOwnProp.call(to, key))
        __defProp(to, key, {
          get: __accessProp.bind(mod, key),
          enumerable: true
        });
  }
  if (canCache)
    cache.set(mod, to);
  return to;
};
var __commonJS = (cb, mod) => () => (mod || cb((mod = { exports: {} }).exports, mod), mod.exports);
var __returnValue = (v) => v;
function __exportSetter(name, newValue) {
  this[name] = __returnValue.bind(null, newValue);
}
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, {
      get: all[name],
      enumerable: true,
      configurable: true,
      set: __exportSetter.bind(all, name)
    });
};

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/applyToPoint.js
var require_applyToPoint = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.applyToPoint = applyToPoint;
  exports.applyToPoints = applyToPoints;
  function applyToPoint(matrix, point) {
    return Array.isArray(point) ? [matrix.a * point[0] + matrix.c * point[1] + matrix.e, matrix.b * point[0] + matrix.d * point[1] + matrix.f] : {
      x: matrix.a * point.x + matrix.c * point.y + matrix.e,
      y: matrix.b * point.x + matrix.d * point.y + matrix.f
    };
  }
  function applyToPoints(matrix, points) {
    return points.map((point) => applyToPoint(matrix, point));
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/fromObject.js
var require_fromObject = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.fromObject = fromObject;
  function fromObject(object) {
    return {
      a: parseFloat(object.a),
      b: parseFloat(object.b),
      c: parseFloat(object.c),
      d: parseFloat(object.d),
      e: parseFloat(object.e),
      f: parseFloat(object.f)
    };
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/fromString.js
var require_fromString = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.fromString = fromString;
  exports.fromStringLegacy = fromStringLegacy;
  var matrixRegex = /^matrix\(\s*([0-9_+-.e]+)\s*,\s*([0-9_+-.e]+)\s*,\s*([0-9_+-.e]+)\s*,\s*([0-9_+-.e]+)\s*,\s*([0-9_+-.e]+)\s*,\s*([0-9_+-.e]+)\s*\)$/i;
  function fromString(string) {
    const parseFloatOrThrow = (number) => {
      const n = parseFloat(number);
      if (Number.isFinite(n))
        return n;
      throw new Error(`'${string}' is not a matrix`);
    };
    const prefix = string.substring(0, 7).toLowerCase();
    const suffix = string.substring(string.length - 1);
    const body = string.substring(7, string.length - 1);
    const elements = body.split(",");
    if (prefix === "matrix(" && suffix === ")" && elements.length === 6) {
      return {
        a: parseFloatOrThrow(elements[0]),
        b: parseFloatOrThrow(elements[1]),
        c: parseFloatOrThrow(elements[2]),
        d: parseFloatOrThrow(elements[3]),
        e: parseFloatOrThrow(elements[4]),
        f: parseFloatOrThrow(elements[5])
      };
    }
    throw new Error(`'${string}' is not a matrix`);
  }
  function fromStringLegacy(string) {
    const parsed = string.match(matrixRegex);
    if (parsed === null || parsed.length < 7)
      throw new Error(`'${string}' is not a matrix`);
    return {
      a: parseFloat(parsed[1]),
      b: parseFloat(parsed[2]),
      c: parseFloat(parsed[3]),
      d: parseFloat(parsed[4]),
      e: parseFloat(parsed[5]),
      f: parseFloat(parsed[6])
    };
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/identity.js
var require_identity = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.identity = identity;
  function identity() {
    return {
      a: 1,
      c: 0,
      e: 0,
      b: 0,
      d: 1,
      f: 0
    };
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/inverse.js
var require_inverse = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.inverse = inverse;
  function inverse(matrix) {
    const {
      a,
      b,
      c,
      d,
      e,
      f
    } = matrix;
    const denom = a * d - b * c;
    return {
      a: d / denom,
      b: b / -denom,
      c: c / -denom,
      d: a / denom,
      e: (d * e - c * f) / -denom,
      f: (b * e - a * f) / denom
    };
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/utils.js
var require_utils = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.isNumeric = isNumeric;
  exports.isObject = isObject;
  exports.isUndefined = isUndefined;
  exports.matchesShape = matchesShape;
  function isUndefined(val) {
    return typeof val === "undefined";
  }
  function isNumeric(n) {
    return typeof n === "number" && !Number.isNaN(n) && Number.isFinite(n);
  }
  function isObject(obj) {
    return typeof obj === "object" && obj !== null && !Array.isArray(obj);
  }
  function matchesShape(obj, keys) {
    return keys.every((key) => (key in obj));
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/isAffineMatrix.js
var require_isAffineMatrix = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.isAffineMatrix = isAffineMatrix;
  var _utils = require_utils();
  function isAffineMatrix(object) {
    return (0, _utils.isObject)(object) && "a" in object && (0, _utils.isNumeric)(object.a) && "b" in object && (0, _utils.isNumeric)(object.b) && "c" in object && (0, _utils.isNumeric)(object.c) && "d" in object && (0, _utils.isNumeric)(object.d) && "e" in object && (0, _utils.isNumeric)(object.e) && "f" in object && (0, _utils.isNumeric)(object.f);
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/translate.js
var require_translate = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.translate = translate;
  function translate(tx, ty = 0) {
    return {
      a: 1,
      c: 0,
      e: tx,
      b: 0,
      d: 1,
      f: ty
    };
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/transform.js
var require_transform = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.compose = compose;
  exports.transform = transform;
  function transform(...matrices) {
    matrices = Array.isArray(matrices[0]) ? matrices[0] : matrices;
    const multiply = (m1, m2) => {
      return {
        a: m1.a * m2.a + m1.c * m2.b,
        c: m1.a * m2.c + m1.c * m2.d,
        e: m1.a * m2.e + m1.c * m2.f + m1.e,
        b: m1.b * m2.a + m1.d * m2.b,
        d: m1.b * m2.c + m1.d * m2.d,
        f: m1.b * m2.e + m1.d * m2.f + m1.f
      };
    };
    switch (matrices.length) {
      case 0:
        throw new Error("no matrices provided");
      case 1:
        return matrices[0];
      case 2:
        return multiply(matrices[0], matrices[1]);
      default: {
        const [m1, m2, ...rest] = matrices;
        const m = multiply(m1, m2);
        return transform(m, ...rest);
      }
    }
  }
  function compose(...matrices) {
    return transform(...matrices);
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/rotate.js
var require_rotate = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.rotate = rotate;
  exports.rotateDEG = rotateDEG;
  var _utils = require_utils();
  var _translate = require_translate();
  var _transform = require_transform();
  var {
    cos,
    sin,
    PI
  } = Math;
  function rotate(angle, cx, cy) {
    const cosAngle = cos(angle);
    const sinAngle = sin(angle);
    const rotationMatrix = {
      a: cosAngle,
      c: -sinAngle,
      e: 0,
      b: sinAngle,
      d: cosAngle,
      f: 0
    };
    if ((0, _utils.isUndefined)(cx) || (0, _utils.isUndefined)(cy)) {
      return rotationMatrix;
    }
    return (0, _transform.transform)([(0, _translate.translate)(cx, cy), rotationMatrix, (0, _translate.translate)(-cx, -cy)]);
  }
  function rotateDEG(angle, cx = undefined, cy = undefined) {
    return rotate(angle * PI / 180, cx, cy);
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/scale.js
var require_scale = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.scale = scale;
  var _utils = require_utils();
  var _translate = require_translate();
  var _transform = require_transform();
  function scale(sx, sy = undefined, cx = undefined, cy = undefined) {
    if ((0, _utils.isUndefined)(sy))
      sy = sx;
    const scaleMatrix = {
      a: sx,
      c: 0,
      e: 0,
      b: 0,
      d: sy,
      f: 0
    };
    if ((0, _utils.isUndefined)(cx) || (0, _utils.isUndefined)(cy)) {
      return scaleMatrix;
    }
    return (0, _transform.transform)([(0, _translate.translate)(cx, cy), scaleMatrix, (0, _translate.translate)(-cx, -cy)]);
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/shear.js
var require_shear = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.shear = shear;
  function shear(shx, shy) {
    return {
      a: 1,
      c: shx,
      e: 0,
      b: shy,
      d: 1,
      f: 0
    };
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/skew.js
var require_skew = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.skew = skew;
  exports.skewDEG = skewDEG;
  var {
    tan
  } = Math;
  function skew(ax, ay) {
    return {
      a: 1,
      c: tan(ax),
      e: 0,
      b: tan(ay),
      d: 1,
      f: 0
    };
  }
  function skewDEG(ax, ay) {
    return skew(ax * Math.PI / 180, ay * Math.PI / 180);
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/toString.js
var require_toString = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.toCSS = toCSS;
  exports.toSVG = toSVG;
  exports.toString = toString;
  function toCSS(matrix) {
    return toString(matrix);
  }
  function toSVG(matrix) {
    return toString(matrix);
  }
  function toString(matrix) {
    return `matrix(${matrix.a},${matrix.b},${matrix.c},${matrix.d},${matrix.e},${matrix.f})`;
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/smoothMatrix.js
var require_smoothMatrix = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.smoothMatrix = smoothMatrix;
  function smoothMatrix(matrix, precision = 10000000000) {
    return {
      a: Math.round(matrix.a * precision) / precision,
      b: Math.round(matrix.b * precision) / precision,
      c: Math.round(matrix.c * precision) / precision,
      d: Math.round(matrix.d * precision) / precision,
      e: Math.round(matrix.e * precision) / precision,
      f: Math.round(matrix.f * precision) / precision
    };
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/fromTriangles.js
var require_fromTriangles = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.fromTriangles = fromTriangles;
  var _inverse = require_inverse();
  var _transform = require_transform();
  var _smoothMatrix = require_smoothMatrix();
  function fromTriangles(t1, t2) {
    const px1 = t1[0].x != null ? t1[0].x : t1[0][0];
    const py1 = t1[0].y != null ? t1[0].y : t1[0][1];
    const px2 = t2[0].x != null ? t2[0].x : t2[0][0];
    const py2 = t2[0].y != null ? t2[0].y : t2[0][1];
    const qx1 = t1[1].x != null ? t1[1].x : t1[1][0];
    const qy1 = t1[1].y != null ? t1[1].y : t1[1][1];
    const qx2 = t2[1].x != null ? t2[1].x : t2[1][0];
    const qy2 = t2[1].y != null ? t2[1].y : t2[1][1];
    const rx1 = t1[2].x != null ? t1[2].x : t1[2][0];
    const ry1 = t1[2].y != null ? t1[2].y : t1[2][1];
    const rx2 = t2[2].x != null ? t2[2].x : t2[2][0];
    const ry2 = t2[2].y != null ? t2[2].y : t2[2][1];
    const r1 = {
      a: px1 - rx1,
      b: py1 - ry1,
      c: qx1 - rx1,
      d: qy1 - ry1,
      e: rx1,
      f: ry1
    };
    const r2 = {
      a: px2 - rx2,
      b: py2 - ry2,
      c: qx2 - rx2,
      d: qy2 - ry2,
      e: rx2,
      f: ry2
    };
    const inverseR1 = (0, _inverse.inverse)(r1);
    const affineMatrix = (0, _transform.transform)([r2, inverseR1]);
    return (0, _smoothMatrix.smoothMatrix)(affineMatrix);
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/fromDefinition.js
var require_fromDefinition = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.fromDefinition = fromDefinition;
  var _fromObject = require_fromObject();
  var _translate = require_translate();
  var _scale = require_scale();
  var _rotate = require_rotate();
  var _skew = require_skew();
  var _shear = require_shear();
  function fromDefinition(definitionOrArrayOfDefinition) {
    return Array.isArray(definitionOrArrayOfDefinition) ? definitionOrArrayOfDefinition.map(mapper) : mapper(definitionOrArrayOfDefinition);
    function mapper(descriptor) {
      switch (descriptor.type) {
        case "matrix":
          if ("a" in descriptor && "b" in descriptor && "c" in descriptor && "d" in descriptor && "e" in descriptor && "f" in descriptor) {
            return (0, _fromObject.fromObject)(descriptor);
          } else {
            throw new Error("MISSING_MANDATORY_PARAM");
          }
        case "translate":
          if (!("tx" in descriptor))
            throw new Error("MISSING_MANDATORY_PARAM");
          if ("ty" in descriptor)
            return (0, _translate.translate)(descriptor.tx, descriptor.ty);
          return (0, _translate.translate)(descriptor.tx);
        case "scale":
          if (!("sx" in descriptor))
            throw new Error("MISSING_MANDATORY_PARAM");
          if ("sy" in descriptor)
            return (0, _scale.scale)(descriptor.sx, descriptor.sy);
          return (0, _scale.scale)(descriptor.sx);
        case "rotate":
          if (!("angle" in descriptor))
            throw new Error("MISSING_MANDATORY_PARAM");
          if ("cx" in descriptor && "cy" in descriptor) {
            return (0, _rotate.rotateDEG)(descriptor.angle, descriptor.cx, descriptor.cy);
          }
          return (0, _rotate.rotateDEG)(descriptor.angle);
        case "skewX":
          if (!("angle" in descriptor))
            throw new Error("MISSING_MANDATORY_PARAM");
          return (0, _skew.skewDEG)(descriptor.angle, 0);
        case "skewY":
          if (!("angle" in descriptor))
            throw new Error("MISSING_MANDATORY_PARAM");
          return (0, _skew.skewDEG)(0, descriptor.angle);
        case "shear":
          if (!(("shx" in descriptor) && ("shy" in descriptor)))
            throw new Error("MISSING_MANDATORY_PARAM");
          return (0, _shear.shear)(descriptor.shx, descriptor.shy);
        default:
          throw new Error("UNSUPPORTED_DESCRIPTOR");
      }
    }
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/fromTransformAttribute.autogenerated.js
var require_fromTransformAttribute_autogenerated = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.SyntaxError = exports.StartRules = undefined;
  exports.parse = peg$parse;

  class peg$SyntaxError extends SyntaxError {
    constructor(message, expected, found, location) {
      super(message);
      this.expected = expected;
      this.found = found;
      this.location = location;
      this.name = "SyntaxError";
    }
    format(sources) {
      let str = "Error: " + this.message;
      if (this.location) {
        let src = null;
        const st = sources.find((s) => s.source === this.location.source);
        if (st) {
          src = st.text.split(/\r\n|\n|\r/g);
        }
        const s = this.location.start;
        const offset_s = this.location.source && typeof this.location.source.offset === "function" ? this.location.source.offset(s) : s;
        const loc = this.location.source + ":" + offset_s.line + ":" + offset_s.column;
        if (src) {
          const e = this.location.end;
          const filler = "".padEnd(offset_s.line.toString().length, " ");
          const line = src[s.line - 1];
          const last = s.line === e.line ? e.column : line.length + 1;
          const hatLen = last - s.column || 1;
          str += `
 --> ` + loc + `
` + filler + ` |
` + offset_s.line + " | " + line + `
` + filler + " | " + "".padEnd(s.column - 1, " ") + "".padEnd(hatLen, "^");
        } else {
          str += `
 at ` + loc;
        }
      }
      return str;
    }
    static buildMessage(expected, found) {
      function hex(ch) {
        return ch.codePointAt(0).toString(16).toUpperCase();
      }
      const nonPrintable = Object.prototype.hasOwnProperty.call(RegExp.prototype, "unicode") ? new RegExp("[\\p{C}\\p{Mn}\\p{Mc}]", "gu") : null;
      function unicodeEscape(s) {
        if (nonPrintable) {
          return s.replace(nonPrintable, (ch) => "\\u{" + hex(ch) + "}");
        }
        return s;
      }
      function literalEscape(s) {
        return unicodeEscape(s.replace(/\\/g, "\\\\").replace(/"/g, "\\\"").replace(/\0/g, "\\0").replace(/\t/g, "\\t").replace(/\n/g, "\\n").replace(/\r/g, "\\r").replace(/[\x00-\x0F]/g, (ch) => "\\x0" + hex(ch)).replace(/[\x10-\x1F\x7F-\x9F]/g, (ch) => "\\x" + hex(ch)));
      }
      function classEscape(s) {
        return unicodeEscape(s.replace(/\\/g, "\\\\").replace(/\]/g, "\\]").replace(/\^/g, "\\^").replace(/-/g, "\\-").replace(/\0/g, "\\0").replace(/\t/g, "\\t").replace(/\n/g, "\\n").replace(/\r/g, "\\r").replace(/[\x00-\x0F]/g, (ch) => "\\x0" + hex(ch)).replace(/[\x10-\x1F\x7F-\x9F]/g, (ch) => "\\x" + hex(ch)));
      }
      const DESCRIBE_EXPECTATION_FNS = {
        literal(expectation) {
          return '"' + literalEscape(expectation.text) + '"';
        },
        class(expectation) {
          const escapedParts = expectation.parts.map((part) => Array.isArray(part) ? classEscape(part[0]) + "-" + classEscape(part[1]) : classEscape(part));
          return "[" + (expectation.inverted ? "^" : "") + escapedParts.join("") + "]" + (expectation.unicode ? "u" : "");
        },
        any() {
          return "any character";
        },
        end() {
          return "end of input";
        },
        other(expectation) {
          return expectation.description;
        }
      };
      function describeExpectation(expectation) {
        return DESCRIBE_EXPECTATION_FNS[expectation.type](expectation);
      }
      function describeExpected(expected) {
        const descriptions = expected.map(describeExpectation);
        descriptions.sort();
        if (descriptions.length > 0) {
          let j = 1;
          for (let i = 1;i < descriptions.length; i++) {
            if (descriptions[i - 1] !== descriptions[i]) {
              descriptions[j] = descriptions[i];
              j++;
            }
          }
          descriptions.length = j;
        }
        switch (descriptions.length) {
          case 1:
            return descriptions[0];
          case 2:
            return descriptions[0] + " or " + descriptions[1];
          default:
            return descriptions.slice(0, -1).join(", ") + ", or " + descriptions[descriptions.length - 1];
        }
      }
      function describeFound(found) {
        return found ? '"' + literalEscape(found) + '"' : "end of input";
      }
      return "Expected " + describeExpected(expected) + " but " + describeFound(found) + " found.";
    }
  }
  exports.SyntaxError = peg$SyntaxError;
  function peg$parse(input, options) {
    options = options !== undefined ? options : {};
    const peg$FAILED = {};
    const peg$source = options.grammarSource;
    const peg$startRuleFunctions = {
      transformList: peg$parsetransformList
    };
    let peg$startRuleFunction = peg$parsetransformList;
    const peg$c0 = "matrix";
    const peg$c1 = "(";
    const peg$c2 = ")";
    const peg$c3 = "translate";
    const peg$c4 = "scale";
    const peg$c5 = "rotate";
    const peg$c6 = "skewX";
    const peg$c7 = "skewY";
    const peg$c8 = ",";
    const peg$c9 = ".";
    const peg$r0 = /^[eE]/;
    const peg$r1 = /^[+\-]/;
    const peg$r2 = /^[0-9]/;
    const peg$r3 = /^[ \t\r\n]/;
    const peg$e0 = peg$literalExpectation("matrix", false);
    const peg$e1 = peg$literalExpectation("(", false);
    const peg$e2 = peg$literalExpectation(")", false);
    const peg$e3 = peg$literalExpectation("translate", false);
    const peg$e4 = peg$literalExpectation("scale", false);
    const peg$e5 = peg$literalExpectation("rotate", false);
    const peg$e6 = peg$literalExpectation("skewX", false);
    const peg$e7 = peg$literalExpectation("skewY", false);
    const peg$e8 = peg$literalExpectation(",", false);
    const peg$e9 = peg$otherExpectation("fractionalConstant");
    const peg$e10 = peg$literalExpectation(".", false);
    const peg$e11 = peg$classExpectation(["e", "E"], false, false, false);
    const peg$e12 = peg$classExpectation(["+", "-"], false, false, false);
    const peg$e13 = peg$classExpectation([["0", "9"]], false, false, false);
    const peg$e14 = peg$classExpectation([" ", "\t", "\r", `
`], false, false, false);
    function peg$f0(ts) {
      return ts;
    }
    function peg$f1(t, ts) {
      return t.concat(ts);
    }
    function peg$f2(a, b, c, d, e, f) {
      return [{
        type: "matrix",
        a,
        b,
        c,
        d,
        e,
        f
      }];
    }
    function peg$f3(tx, ty) {
      var t = {
        type: "translate",
        tx
      };
      if (ty)
        t.ty = ty;
      return [t];
    }
    function peg$f4(sx, sy) {
      var s = {
        type: "scale",
        sx
      };
      if (sy)
        s.sy = sy;
      return [s];
    }
    function peg$f5(angle, c) {
      var r = {
        type: "rotate",
        angle
      };
      if (c) {
        r.cx = c[0];
        r.cy = c[1];
      }
      return [r];
    }
    function peg$f6(angle) {
      return [{
        type: "skewX",
        angle
      }];
    }
    function peg$f7(angle) {
      return [{
        type: "skewY",
        angle
      }];
    }
    function peg$f8(f) {
      return parseFloat(f.join(""));
    }
    function peg$f9(i) {
      return parseInt(i.join(""));
    }
    function peg$f10(n) {
      return n;
    }
    function peg$f11(n1, n2) {
      return [n1, n2];
    }
    function peg$f12(ds) {
      return ds.join("");
    }
    function peg$f13(f, e) {
      return [f, e || null].join("");
    }
    function peg$f14(d, e) {
      return [d, e].join("");
    }
    function peg$f15(d1, d2) {
      return [d1 ? d1.join("") : null, ".", d2.join("")].join("");
    }
    function peg$f16(d) {
      return d.join("");
    }
    function peg$f17(s, d) {
      return ["e", s, d.join("")].join("");
    }
    let peg$currPos = options.peg$currPos | 0;
    let peg$savedPos = peg$currPos;
    const peg$posDetailsCache = [{
      line: 1,
      column: 1
    }];
    let peg$maxFailPos = peg$currPos;
    let peg$maxFailExpected = options.peg$maxFailExpected || [];
    let peg$silentFails = options.peg$silentFails | 0;
    let peg$result;
    if (options.startRule) {
      if (!(options.startRule in peg$startRuleFunctions)) {
        throw new Error(`Can't start parsing from rule "` + options.startRule + '".');
      }
      peg$startRuleFunction = peg$startRuleFunctions[options.startRule];
    }
    function text() {
      return input.substring(peg$savedPos, peg$currPos);
    }
    function offset() {
      return peg$savedPos;
    }
    function range() {
      return {
        source: peg$source,
        start: peg$savedPos,
        end: peg$currPos
      };
    }
    function location() {
      return peg$computeLocation(peg$savedPos, peg$currPos);
    }
    function expected(description, location) {
      location = location !== undefined ? location : peg$computeLocation(peg$savedPos, peg$currPos);
      throw peg$buildStructuredError([peg$otherExpectation(description)], input.substring(peg$savedPos, peg$currPos), location);
    }
    function error(message, location) {
      location = location !== undefined ? location : peg$computeLocation(peg$savedPos, peg$currPos);
      throw peg$buildSimpleError(message, location);
    }
    function peg$getUnicode(pos = peg$currPos) {
      const cp = input.codePointAt(pos);
      if (cp === undefined) {
        return "";
      }
      return String.fromCodePoint(cp);
    }
    function peg$literalExpectation(text, ignoreCase) {
      return {
        type: "literal",
        text,
        ignoreCase
      };
    }
    function peg$classExpectation(parts, inverted, ignoreCase, unicode) {
      return {
        type: "class",
        parts,
        inverted,
        ignoreCase,
        unicode
      };
    }
    function peg$anyExpectation() {
      return {
        type: "any"
      };
    }
    function peg$endExpectation() {
      return {
        type: "end"
      };
    }
    function peg$otherExpectation(description) {
      return {
        type: "other",
        description
      };
    }
    function peg$computePosDetails(pos) {
      let details = peg$posDetailsCache[pos];
      let p;
      if (details) {
        return details;
      } else {
        if (pos >= peg$posDetailsCache.length) {
          p = peg$posDetailsCache.length - 1;
        } else {
          p = pos;
          while (!peg$posDetailsCache[--p]) {}
        }
        details = peg$posDetailsCache[p];
        details = {
          line: details.line,
          column: details.column
        };
        while (p < pos) {
          if (input.charCodeAt(p) === 10) {
            details.line++;
            details.column = 1;
          } else {
            details.column++;
          }
          p++;
        }
        peg$posDetailsCache[pos] = details;
        return details;
      }
    }
    function peg$computeLocation(startPos, endPos, offset) {
      const startPosDetails = peg$computePosDetails(startPos);
      const endPosDetails = peg$computePosDetails(endPos);
      const res = {
        source: peg$source,
        start: {
          offset: startPos,
          line: startPosDetails.line,
          column: startPosDetails.column
        },
        end: {
          offset: endPos,
          line: endPosDetails.line,
          column: endPosDetails.column
        }
      };
      if (offset && peg$source && typeof peg$source.offset === "function") {
        res.start = peg$source.offset(res.start);
        res.end = peg$source.offset(res.end);
      }
      return res;
    }
    function peg$fail(expected) {
      if (peg$currPos < peg$maxFailPos) {
        return;
      }
      if (peg$currPos > peg$maxFailPos) {
        peg$maxFailPos = peg$currPos;
        peg$maxFailExpected = [];
      }
      peg$maxFailExpected.push(expected);
    }
    function peg$buildSimpleError(message, location) {
      return new peg$SyntaxError(message, null, null, location);
    }
    function peg$buildStructuredError(expected, found, location) {
      return new peg$SyntaxError(peg$SyntaxError.buildMessage(expected, found), expected, found, location);
    }
    function peg$parsetransformList() {
      let s0, s1, s2, s3, s4;
      s0 = peg$currPos;
      s1 = [];
      s2 = peg$parsewsp();
      while (s2 !== peg$FAILED) {
        s1.push(s2);
        s2 = peg$parsewsp();
      }
      s2 = peg$parsetransforms();
      if (s2 === peg$FAILED) {
        s2 = null;
      }
      s3 = [];
      s4 = peg$parsewsp();
      while (s4 !== peg$FAILED) {
        s3.push(s4);
        s4 = peg$parsewsp();
      }
      peg$savedPos = s0;
      s0 = peg$f0(s2);
      return s0;
    }
    function peg$parsetransforms() {
      let s0, s1, s2, s3;
      s0 = peg$currPos;
      s1 = peg$parsetransform();
      if (s1 !== peg$FAILED) {
        s2 = [];
        s3 = peg$parsecommaWsp();
        if (s3 !== peg$FAILED) {
          while (s3 !== peg$FAILED) {
            s2.push(s3);
            s3 = peg$parsecommaWsp();
          }
        } else {
          s2 = peg$FAILED;
        }
        if (s2 !== peg$FAILED) {
          s3 = peg$parsetransforms();
          if (s3 !== peg$FAILED) {
            peg$savedPos = s0;
            s0 = peg$f1(s1, s3);
          } else {
            peg$currPos = s0;
            s0 = peg$FAILED;
          }
        } else {
          peg$currPos = s0;
          s0 = peg$FAILED;
        }
      } else {
        peg$currPos = s0;
        s0 = peg$FAILED;
      }
      if (s0 === peg$FAILED) {
        s0 = peg$parsetransform();
      }
      return s0;
    }
    function peg$parsetransform() {
      let s0;
      s0 = peg$parsematrix();
      if (s0 === peg$FAILED) {
        s0 = peg$parsetranslate();
        if (s0 === peg$FAILED) {
          s0 = peg$parsescale();
          if (s0 === peg$FAILED) {
            s0 = peg$parserotate();
            if (s0 === peg$FAILED) {
              s0 = peg$parseskewX();
              if (s0 === peg$FAILED) {
                s0 = peg$parseskewY();
              }
            }
          }
        }
      }
      return s0;
    }
    function peg$parsematrix() {
      let s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17;
      s0 = peg$currPos;
      if (input.substr(peg$currPos, 6) === peg$c0) {
        s1 = peg$c0;
        peg$currPos += 6;
      } else {
        s1 = peg$FAILED;
        if (peg$silentFails === 0) {
          peg$fail(peg$e0);
        }
      }
      if (s1 !== peg$FAILED) {
        s2 = [];
        s3 = peg$parsewsp();
        while (s3 !== peg$FAILED) {
          s2.push(s3);
          s3 = peg$parsewsp();
        }
        if (input.charCodeAt(peg$currPos) === 40) {
          s3 = peg$c1;
          peg$currPos++;
        } else {
          s3 = peg$FAILED;
          if (peg$silentFails === 0) {
            peg$fail(peg$e1);
          }
        }
        if (s3 !== peg$FAILED) {
          s4 = [];
          s5 = peg$parsewsp();
          while (s5 !== peg$FAILED) {
            s4.push(s5);
            s5 = peg$parsewsp();
          }
          s5 = peg$parsenumber();
          if (s5 !== peg$FAILED) {
            s6 = peg$parsecommaWsp();
            if (s6 !== peg$FAILED) {
              s7 = peg$parsenumber();
              if (s7 !== peg$FAILED) {
                s8 = peg$parsecommaWsp();
                if (s8 !== peg$FAILED) {
                  s9 = peg$parsenumber();
                  if (s9 !== peg$FAILED) {
                    s10 = peg$parsecommaWsp();
                    if (s10 !== peg$FAILED) {
                      s11 = peg$parsenumber();
                      if (s11 !== peg$FAILED) {
                        s12 = peg$parsecommaWsp();
                        if (s12 !== peg$FAILED) {
                          s13 = peg$parsenumber();
                          if (s13 !== peg$FAILED) {
                            s14 = peg$parsecommaWsp();
                            if (s14 !== peg$FAILED) {
                              s15 = peg$parsenumber();
                              if (s15 !== peg$FAILED) {
                                s16 = [];
                                s17 = peg$parsewsp();
                                while (s17 !== peg$FAILED) {
                                  s16.push(s17);
                                  s17 = peg$parsewsp();
                                }
                                if (input.charCodeAt(peg$currPos) === 41) {
                                  s17 = peg$c2;
                                  peg$currPos++;
                                } else {
                                  s17 = peg$FAILED;
                                  if (peg$silentFails === 0) {
                                    peg$fail(peg$e2);
                                  }
                                }
                                if (s17 !== peg$FAILED) {
                                  peg$savedPos = s0;
                                  s0 = peg$f2(s5, s7, s9, s11, s13, s15);
                                } else {
                                  peg$currPos = s0;
                                  s0 = peg$FAILED;
                                }
                              } else {
                                peg$currPos = s0;
                                s0 = peg$FAILED;
                              }
                            } else {
                              peg$currPos = s0;
                              s0 = peg$FAILED;
                            }
                          } else {
                            peg$currPos = s0;
                            s0 = peg$FAILED;
                          }
                        } else {
                          peg$currPos = s0;
                          s0 = peg$FAILED;
                        }
                      } else {
                        peg$currPos = s0;
                        s0 = peg$FAILED;
                      }
                    } else {
                      peg$currPos = s0;
                      s0 = peg$FAILED;
                    }
                  } else {
                    peg$currPos = s0;
                    s0 = peg$FAILED;
                  }
                } else {
                  peg$currPos = s0;
                  s0 = peg$FAILED;
                }
              } else {
                peg$currPos = s0;
                s0 = peg$FAILED;
              }
            } else {
              peg$currPos = s0;
              s0 = peg$FAILED;
            }
          } else {
            peg$currPos = s0;
            s0 = peg$FAILED;
          }
        } else {
          peg$currPos = s0;
          s0 = peg$FAILED;
        }
      } else {
        peg$currPos = s0;
        s0 = peg$FAILED;
      }
      return s0;
    }
    function peg$parsetranslate() {
      let s0, s1, s2, s3, s4, s5, s6, s7, s8;
      s0 = peg$currPos;
      if (input.substr(peg$currPos, 9) === peg$c3) {
        s1 = peg$c3;
        peg$currPos += 9;
      } else {
        s1 = peg$FAILED;
        if (peg$silentFails === 0) {
          peg$fail(peg$e3);
        }
      }
      if (s1 !== peg$FAILED) {
        s2 = [];
        s3 = peg$parsewsp();
        while (s3 !== peg$FAILED) {
          s2.push(s3);
          s3 = peg$parsewsp();
        }
        if (input.charCodeAt(peg$currPos) === 40) {
          s3 = peg$c1;
          peg$currPos++;
        } else {
          s3 = peg$FAILED;
          if (peg$silentFails === 0) {
            peg$fail(peg$e1);
          }
        }
        if (s3 !== peg$FAILED) {
          s4 = [];
          s5 = peg$parsewsp();
          while (s5 !== peg$FAILED) {
            s4.push(s5);
            s5 = peg$parsewsp();
          }
          s5 = peg$parsenumber();
          if (s5 !== peg$FAILED) {
            s6 = peg$parsecommaWspNumber();
            if (s6 === peg$FAILED) {
              s6 = null;
            }
            s7 = [];
            s8 = peg$parsewsp();
            while (s8 !== peg$FAILED) {
              s7.push(s8);
              s8 = peg$parsewsp();
            }
            if (input.charCodeAt(peg$currPos) === 41) {
              s8 = peg$c2;
              peg$currPos++;
            } else {
              s8 = peg$FAILED;
              if (peg$silentFails === 0) {
                peg$fail(peg$e2);
              }
            }
            if (s8 !== peg$FAILED) {
              peg$savedPos = s0;
              s0 = peg$f3(s5, s6);
            } else {
              peg$currPos = s0;
              s0 = peg$FAILED;
            }
          } else {
            peg$currPos = s0;
            s0 = peg$FAILED;
          }
        } else {
          peg$currPos = s0;
          s0 = peg$FAILED;
        }
      } else {
        peg$currPos = s0;
        s0 = peg$FAILED;
      }
      return s0;
    }
    function peg$parsescale() {
      let s0, s1, s2, s3, s4, s5, s6, s7, s8;
      s0 = peg$currPos;
      if (input.substr(peg$currPos, 5) === peg$c4) {
        s1 = peg$c4;
        peg$currPos += 5;
      } else {
        s1 = peg$FAILED;
        if (peg$silentFails === 0) {
          peg$fail(peg$e4);
        }
      }
      if (s1 !== peg$FAILED) {
        s2 = [];
        s3 = peg$parsewsp();
        while (s3 !== peg$FAILED) {
          s2.push(s3);
          s3 = peg$parsewsp();
        }
        if (input.charCodeAt(peg$currPos) === 40) {
          s3 = peg$c1;
          peg$currPos++;
        } else {
          s3 = peg$FAILED;
          if (peg$silentFails === 0) {
            peg$fail(peg$e1);
          }
        }
        if (s3 !== peg$FAILED) {
          s4 = [];
          s5 = peg$parsewsp();
          while (s5 !== peg$FAILED) {
            s4.push(s5);
            s5 = peg$parsewsp();
          }
          s5 = peg$parsenumber();
          if (s5 !== peg$FAILED) {
            s6 = peg$parsecommaWspNumber();
            if (s6 === peg$FAILED) {
              s6 = null;
            }
            s7 = [];
            s8 = peg$parsewsp();
            while (s8 !== peg$FAILED) {
              s7.push(s8);
              s8 = peg$parsewsp();
            }
            if (input.charCodeAt(peg$currPos) === 41) {
              s8 = peg$c2;
              peg$currPos++;
            } else {
              s8 = peg$FAILED;
              if (peg$silentFails === 0) {
                peg$fail(peg$e2);
              }
            }
            if (s8 !== peg$FAILED) {
              peg$savedPos = s0;
              s0 = peg$f4(s5, s6);
            } else {
              peg$currPos = s0;
              s0 = peg$FAILED;
            }
          } else {
            peg$currPos = s0;
            s0 = peg$FAILED;
          }
        } else {
          peg$currPos = s0;
          s0 = peg$FAILED;
        }
      } else {
        peg$currPos = s0;
        s0 = peg$FAILED;
      }
      return s0;
    }
    function peg$parserotate() {
      let s0, s1, s2, s3, s4, s5, s6, s7, s8;
      s0 = peg$currPos;
      if (input.substr(peg$currPos, 6) === peg$c5) {
        s1 = peg$c5;
        peg$currPos += 6;
      } else {
        s1 = peg$FAILED;
        if (peg$silentFails === 0) {
          peg$fail(peg$e5);
        }
      }
      if (s1 !== peg$FAILED) {
        s2 = [];
        s3 = peg$parsewsp();
        while (s3 !== peg$FAILED) {
          s2.push(s3);
          s3 = peg$parsewsp();
        }
        if (input.charCodeAt(peg$currPos) === 40) {
          s3 = peg$c1;
          peg$currPos++;
        } else {
          s3 = peg$FAILED;
          if (peg$silentFails === 0) {
            peg$fail(peg$e1);
          }
        }
        if (s3 !== peg$FAILED) {
          s4 = [];
          s5 = peg$parsewsp();
          while (s5 !== peg$FAILED) {
            s4.push(s5);
            s5 = peg$parsewsp();
          }
          s5 = peg$parsenumber();
          if (s5 !== peg$FAILED) {
            s6 = peg$parsecommaWspTwoNumbers();
            if (s6 === peg$FAILED) {
              s6 = null;
            }
            s7 = [];
            s8 = peg$parsewsp();
            while (s8 !== peg$FAILED) {
              s7.push(s8);
              s8 = peg$parsewsp();
            }
            if (input.charCodeAt(peg$currPos) === 41) {
              s8 = peg$c2;
              peg$currPos++;
            } else {
              s8 = peg$FAILED;
              if (peg$silentFails === 0) {
                peg$fail(peg$e2);
              }
            }
            if (s8 !== peg$FAILED) {
              peg$savedPos = s0;
              s0 = peg$f5(s5, s6);
            } else {
              peg$currPos = s0;
              s0 = peg$FAILED;
            }
          } else {
            peg$currPos = s0;
            s0 = peg$FAILED;
          }
        } else {
          peg$currPos = s0;
          s0 = peg$FAILED;
        }
      } else {
        peg$currPos = s0;
        s0 = peg$FAILED;
      }
      return s0;
    }
    function peg$parseskewX() {
      let s0, s1, s2, s3, s4, s5, s6, s7;
      s0 = peg$currPos;
      if (input.substr(peg$currPos, 5) === peg$c6) {
        s1 = peg$c6;
        peg$currPos += 5;
      } else {
        s1 = peg$FAILED;
        if (peg$silentFails === 0) {
          peg$fail(peg$e6);
        }
      }
      if (s1 !== peg$FAILED) {
        s2 = [];
        s3 = peg$parsewsp();
        while (s3 !== peg$FAILED) {
          s2.push(s3);
          s3 = peg$parsewsp();
        }
        if (input.charCodeAt(peg$currPos) === 40) {
          s3 = peg$c1;
          peg$currPos++;
        } else {
          s3 = peg$FAILED;
          if (peg$silentFails === 0) {
            peg$fail(peg$e1);
          }
        }
        if (s3 !== peg$FAILED) {
          s4 = [];
          s5 = peg$parsewsp();
          while (s5 !== peg$FAILED) {
            s4.push(s5);
            s5 = peg$parsewsp();
          }
          s5 = peg$parsenumber();
          if (s5 !== peg$FAILED) {
            s6 = [];
            s7 = peg$parsewsp();
            while (s7 !== peg$FAILED) {
              s6.push(s7);
              s7 = peg$parsewsp();
            }
            if (input.charCodeAt(peg$currPos) === 41) {
              s7 = peg$c2;
              peg$currPos++;
            } else {
              s7 = peg$FAILED;
              if (peg$silentFails === 0) {
                peg$fail(peg$e2);
              }
            }
            if (s7 !== peg$FAILED) {
              peg$savedPos = s0;
              s0 = peg$f6(s5);
            } else {
              peg$currPos = s0;
              s0 = peg$FAILED;
            }
          } else {
            peg$currPos = s0;
            s0 = peg$FAILED;
          }
        } else {
          peg$currPos = s0;
          s0 = peg$FAILED;
        }
      } else {
        peg$currPos = s0;
        s0 = peg$FAILED;
      }
      return s0;
    }
    function peg$parseskewY() {
      let s0, s1, s2, s3, s4, s5, s6, s7;
      s0 = peg$currPos;
      if (input.substr(peg$currPos, 5) === peg$c7) {
        s1 = peg$c7;
        peg$currPos += 5;
      } else {
        s1 = peg$FAILED;
        if (peg$silentFails === 0) {
          peg$fail(peg$e7);
        }
      }
      if (s1 !== peg$FAILED) {
        s2 = [];
        s3 = peg$parsewsp();
        while (s3 !== peg$FAILED) {
          s2.push(s3);
          s3 = peg$parsewsp();
        }
        if (input.charCodeAt(peg$currPos) === 40) {
          s3 = peg$c1;
          peg$currPos++;
        } else {
          s3 = peg$FAILED;
          if (peg$silentFails === 0) {
            peg$fail(peg$e1);
          }
        }
        if (s3 !== peg$FAILED) {
          s4 = [];
          s5 = peg$parsewsp();
          while (s5 !== peg$FAILED) {
            s4.push(s5);
            s5 = peg$parsewsp();
          }
          s5 = peg$parsenumber();
          if (s5 !== peg$FAILED) {
            s6 = [];
            s7 = peg$parsewsp();
            while (s7 !== peg$FAILED) {
              s6.push(s7);
              s7 = peg$parsewsp();
            }
            if (input.charCodeAt(peg$currPos) === 41) {
              s7 = peg$c2;
              peg$currPos++;
            } else {
              s7 = peg$FAILED;
              if (peg$silentFails === 0) {
                peg$fail(peg$e2);
              }
            }
            if (s7 !== peg$FAILED) {
              peg$savedPos = s0;
              s0 = peg$f7(s5);
            } else {
              peg$currPos = s0;
              s0 = peg$FAILED;
            }
          } else {
            peg$currPos = s0;
            s0 = peg$FAILED;
          }
        } else {
          peg$currPos = s0;
          s0 = peg$FAILED;
        }
      } else {
        peg$currPos = s0;
        s0 = peg$FAILED;
      }
      return s0;
    }
    function peg$parsenumber() {
      let s0, s1, s2, s3;
      s0 = peg$currPos;
      s1 = peg$currPos;
      s2 = peg$parsesign();
      if (s2 === peg$FAILED) {
        s2 = null;
      }
      s3 = peg$parsefloatingPointConstant();
      if (s3 !== peg$FAILED) {
        s2 = [s2, s3];
        s1 = s2;
      } else {
        peg$currPos = s1;
        s1 = peg$FAILED;
      }
      if (s1 !== peg$FAILED) {
        peg$savedPos = s0;
        s1 = peg$f8(s1);
      }
      s0 = s1;
      if (s0 === peg$FAILED) {
        s0 = peg$currPos;
        s1 = peg$currPos;
        s2 = peg$parsesign();
        if (s2 === peg$FAILED) {
          s2 = null;
        }
        s3 = peg$parseintegerConstant();
        if (s3 !== peg$FAILED) {
          s2 = [s2, s3];
          s1 = s2;
        } else {
          peg$currPos = s1;
          s1 = peg$FAILED;
        }
        if (s1 !== peg$FAILED) {
          peg$savedPos = s0;
          s1 = peg$f9(s1);
        }
        s0 = s1;
      }
      return s0;
    }
    function peg$parsecommaWspNumber() {
      let s0, s1, s2;
      s0 = peg$currPos;
      s1 = peg$parsecommaWsp();
      if (s1 !== peg$FAILED) {
        s2 = peg$parsenumber();
        if (s2 !== peg$FAILED) {
          peg$savedPos = s0;
          s0 = peg$f10(s2);
        } else {
          peg$currPos = s0;
          s0 = peg$FAILED;
        }
      } else {
        peg$currPos = s0;
        s0 = peg$FAILED;
      }
      return s0;
    }
    function peg$parsecommaWspTwoNumbers() {
      let s0, s1, s2, s3, s4;
      s0 = peg$currPos;
      s1 = peg$parsecommaWsp();
      if (s1 !== peg$FAILED) {
        s2 = peg$parsenumber();
        if (s2 !== peg$FAILED) {
          s3 = peg$parsecommaWsp();
          if (s3 !== peg$FAILED) {
            s4 = peg$parsenumber();
            if (s4 !== peg$FAILED) {
              peg$savedPos = s0;
              s0 = peg$f11(s2, s4);
            } else {
              peg$currPos = s0;
              s0 = peg$FAILED;
            }
          } else {
            peg$currPos = s0;
            s0 = peg$FAILED;
          }
        } else {
          peg$currPos = s0;
          s0 = peg$FAILED;
        }
      } else {
        peg$currPos = s0;
        s0 = peg$FAILED;
      }
      return s0;
    }
    function peg$parsecommaWsp() {
      let s0, s1, s2, s3, s4;
      s0 = peg$currPos;
      s1 = [];
      s2 = peg$parsewsp();
      if (s2 !== peg$FAILED) {
        while (s2 !== peg$FAILED) {
          s1.push(s2);
          s2 = peg$parsewsp();
        }
      } else {
        s1 = peg$FAILED;
      }
      if (s1 !== peg$FAILED) {
        s2 = peg$parsecomma();
        if (s2 === peg$FAILED) {
          s2 = null;
        }
        s3 = [];
        s4 = peg$parsewsp();
        while (s4 !== peg$FAILED) {
          s3.push(s4);
          s4 = peg$parsewsp();
        }
        s1 = [s1, s2, s3];
        s0 = s1;
      } else {
        peg$currPos = s0;
        s0 = peg$FAILED;
      }
      if (s0 === peg$FAILED) {
        s0 = peg$currPos;
        s1 = peg$parsecomma();
        if (s1 !== peg$FAILED) {
          s2 = [];
          s3 = peg$parsewsp();
          while (s3 !== peg$FAILED) {
            s2.push(s3);
            s3 = peg$parsewsp();
          }
          s1 = [s1, s2];
          s0 = s1;
        } else {
          peg$currPos = s0;
          s0 = peg$FAILED;
        }
      }
      return s0;
    }
    function peg$parsecomma() {
      let s0;
      if (input.charCodeAt(peg$currPos) === 44) {
        s0 = peg$c8;
        peg$currPos++;
      } else {
        s0 = peg$FAILED;
        if (peg$silentFails === 0) {
          peg$fail(peg$e8);
        }
      }
      return s0;
    }
    function peg$parseintegerConstant() {
      let s0, s1;
      s0 = peg$currPos;
      s1 = peg$parsedigitSequence();
      if (s1 !== peg$FAILED) {
        peg$savedPos = s0;
        s1 = peg$f12(s1);
      }
      s0 = s1;
      return s0;
    }
    function peg$parsefloatingPointConstant() {
      let s0, s1, s2;
      s0 = peg$currPos;
      s1 = peg$parsefractionalConstant();
      if (s1 !== peg$FAILED) {
        s2 = peg$parseexponent();
        if (s2 === peg$FAILED) {
          s2 = null;
        }
        peg$savedPos = s0;
        s0 = peg$f13(s1, s2);
      } else {
        peg$currPos = s0;
        s0 = peg$FAILED;
      }
      if (s0 === peg$FAILED) {
        s0 = peg$currPos;
        s1 = peg$parsedigitSequence();
        if (s1 !== peg$FAILED) {
          s2 = peg$parseexponent();
          if (s2 !== peg$FAILED) {
            peg$savedPos = s0;
            s0 = peg$f14(s1, s2);
          } else {
            peg$currPos = s0;
            s0 = peg$FAILED;
          }
        } else {
          peg$currPos = s0;
          s0 = peg$FAILED;
        }
      }
      return s0;
    }
    function peg$parsefractionalConstant() {
      let s0, s1, s2, s3;
      peg$silentFails++;
      s0 = peg$currPos;
      s1 = peg$parsedigitSequence();
      if (s1 === peg$FAILED) {
        s1 = null;
      }
      if (input.charCodeAt(peg$currPos) === 46) {
        s2 = peg$c9;
        peg$currPos++;
      } else {
        s2 = peg$FAILED;
        if (peg$silentFails === 0) {
          peg$fail(peg$e10);
        }
      }
      if (s2 !== peg$FAILED) {
        s3 = peg$parsedigitSequence();
        if (s3 !== peg$FAILED) {
          peg$savedPos = s0;
          s0 = peg$f15(s1, s3);
        } else {
          peg$currPos = s0;
          s0 = peg$FAILED;
        }
      } else {
        peg$currPos = s0;
        s0 = peg$FAILED;
      }
      if (s0 === peg$FAILED) {
        s0 = peg$currPos;
        s1 = peg$parsedigitSequence();
        if (s1 !== peg$FAILED) {
          if (input.charCodeAt(peg$currPos) === 46) {
            s2 = peg$c9;
            peg$currPos++;
          } else {
            s2 = peg$FAILED;
            if (peg$silentFails === 0) {
              peg$fail(peg$e10);
            }
          }
          if (s2 !== peg$FAILED) {
            peg$savedPos = s0;
            s0 = peg$f16(s1);
          } else {
            peg$currPos = s0;
            s0 = peg$FAILED;
          }
        } else {
          peg$currPos = s0;
          s0 = peg$FAILED;
        }
      }
      peg$silentFails--;
      if (s0 === peg$FAILED) {
        s1 = peg$FAILED;
        if (peg$silentFails === 0) {
          peg$fail(peg$e9);
        }
      }
      return s0;
    }
    function peg$parseexponent() {
      let s0, s1, s2, s3;
      s0 = peg$currPos;
      s1 = input.charAt(peg$currPos);
      if (peg$r0.test(s1)) {
        peg$currPos++;
      } else {
        s1 = peg$FAILED;
        if (peg$silentFails === 0) {
          peg$fail(peg$e11);
        }
      }
      if (s1 !== peg$FAILED) {
        s2 = peg$parsesign();
        if (s2 === peg$FAILED) {
          s2 = null;
        }
        s3 = peg$parsedigitSequence();
        if (s3 !== peg$FAILED) {
          peg$savedPos = s0;
          s0 = peg$f17(s2, s3);
        } else {
          peg$currPos = s0;
          s0 = peg$FAILED;
        }
      } else {
        peg$currPos = s0;
        s0 = peg$FAILED;
      }
      return s0;
    }
    function peg$parsesign() {
      let s0;
      s0 = input.charAt(peg$currPos);
      if (peg$r1.test(s0)) {
        peg$currPos++;
      } else {
        s0 = peg$FAILED;
        if (peg$silentFails === 0) {
          peg$fail(peg$e12);
        }
      }
      return s0;
    }
    function peg$parsedigitSequence() {
      let s0, s1;
      s0 = [];
      s1 = peg$parsedigit();
      if (s1 !== peg$FAILED) {
        while (s1 !== peg$FAILED) {
          s0.push(s1);
          s1 = peg$parsedigit();
        }
      } else {
        s0 = peg$FAILED;
      }
      return s0;
    }
    function peg$parsedigit() {
      let s0;
      s0 = input.charAt(peg$currPos);
      if (peg$r2.test(s0)) {
        peg$currPos++;
      } else {
        s0 = peg$FAILED;
        if (peg$silentFails === 0) {
          peg$fail(peg$e13);
        }
      }
      return s0;
    }
    function peg$parsewsp() {
      let s0;
      s0 = input.charAt(peg$currPos);
      if (peg$r3.test(s0)) {
        peg$currPos++;
      } else {
        s0 = peg$FAILED;
        if (peg$silentFails === 0) {
          peg$fail(peg$e14);
        }
      }
      return s0;
    }
    peg$result = peg$startRuleFunction();
    const peg$success = peg$result !== peg$FAILED && peg$currPos === input.length;
    function peg$throw() {
      if (peg$result !== peg$FAILED && peg$currPos < input.length) {
        peg$fail(peg$endExpectation());
      }
      throw peg$buildStructuredError(peg$maxFailExpected, peg$maxFailPos < input.length ? peg$getUnicode(peg$maxFailPos) : null, peg$maxFailPos < input.length ? peg$computeLocation(peg$maxFailPos, peg$maxFailPos + 1) : peg$computeLocation(peg$maxFailPos, peg$maxFailPos));
    }
    if (options.peg$library) {
      return {
        peg$result,
        peg$currPos,
        peg$FAILED,
        peg$maxFailExpected,
        peg$maxFailPos,
        peg$success,
        peg$throw: peg$success ? undefined : peg$throw
      };
    }
    if (peg$success) {
      return peg$result;
    } else {
      peg$throw();
    }
  }
  var peg$allowedStartRules = exports.StartRules = ["transformList"];
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/fromTransformAttribute.js
var require_fromTransformAttribute = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.fromTransformAttribute = fromTransformAttribute;
  var _fromTransformAttribute = require_fromTransformAttribute_autogenerated();
  function fromTransformAttribute(transformString) {
    return (0, _fromTransformAttribute.parse)(transformString);
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/decompose.js
var require_decompose = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.decomposeTSR = decomposeTSR;
  var _scale = require_scale();
  var _transform = require_transform();
  function decomposeTSR(matrix, flipX = false, flipY = false) {
    if (flipX) {
      if (flipY) {
        matrix = (0, _transform.compose)(matrix, (0, _scale.scale)(-1, -1));
      } else {
        matrix = (0, _transform.compose)(matrix, (0, _scale.scale)(1, -1));
      }
    } else if (flipY) {
      matrix = (0, _transform.compose)(matrix, (0, _scale.scale)(-1, 1));
    }
    const a = matrix.a;
    const b = matrix.b;
    const c = matrix.c;
    const d = matrix.d;
    let scaleX, scaleY, rotation;
    if (a !== 0 || c !== 0) {
      const hypotAc = Math.hypot(a, c);
      scaleX = hypotAc;
      scaleY = (a * d - b * c) / hypotAc;
      const acos = Math.acos(a / hypotAc);
      rotation = c > 0 ? -acos : acos;
    } else if (b !== 0 || d !== 0) {
      const hypotBd = Math.hypot(b, d);
      scaleX = (a * d - b * c) / hypotBd;
      scaleY = hypotBd;
      const acos = Math.acos(b / hypotBd);
      rotation = Math.PI / 2 + (d > 0 ? -acos : acos);
    } else {
      scaleX = 0;
      scaleY = 0;
      rotation = 0;
    }
    if (flipY) {
      scaleX = -scaleX;
    }
    if (flipX) {
      scaleY = -scaleY;
    }
    return {
      translate: {
        tx: matrix.e,
        ty: matrix.f
      },
      scale: {
        sx: scaleX,
        sy: scaleY
      },
      rotation: {
        angle: rotation
      }
    };
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/flip.js
var require_flip = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.flipOrigin = flipOrigin;
  exports.flipX = flipX;
  exports.flipY = flipY;
  function flipX() {
    return {
      a: 1,
      c: 0,
      e: 0,
      b: 0,
      d: -1,
      f: 0
    };
  }
  function flipY() {
    return {
      a: -1,
      c: 0,
      e: 0,
      b: 0,
      d: 1,
      f: 0
    };
  }
  function flipOrigin() {
    return {
      a: -1,
      c: 0,
      e: 0,
      b: 0,
      d: -1,
      f: 0
    };
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/fromMovingPoints.js
var require_fromMovingPoints = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.fromOneMovingPoint = fromOneMovingPoint;
  exports.fromTwoMovingPoints = fromTwoMovingPoints;
  var _translate = require_translate();
  var _applyToPoint = require_applyToPoint();
  var _rotate = require_rotate();
  var _scale = require_scale();
  var _transform = require_transform();
  function fromOneMovingPoint(startingPoint, endingPoint) {
    const tx = endingPoint.x - startingPoint.x;
    const ty = endingPoint.y - startingPoint.y;
    return (0, _translate.translate)(tx, ty);
  }
  function fromTwoMovingPoints(startingPoint1, startingPoint2, endingPoint1, endingPoint2) {
    const translationMatrix = fromOneMovingPoint(startingPoint1, endingPoint1);
    const pointA = (0, _applyToPoint.applyToPoint)(translationMatrix, startingPoint2);
    const center = endingPoint1;
    const pointB = endingPoint2;
    const angle = Math.atan2(pointB.y - center.y, pointB.x - center.x) - Math.atan2(pointA.y - center.y, pointA.x - center.x);
    const rotationMatrix = (0, _rotate.rotate)(angle, center.x, center.y);
    const d1 = Math.sqrt(Math.pow(pointA.x - center.x, 2) + Math.pow(pointA.y - center.y, 2));
    const d2 = Math.sqrt(Math.pow(pointB.x - center.x, 2) + Math.pow(pointB.y - center.y, 2));
    const scalingLevel = d2 / d1;
    const scalingMatrix = (0, _scale.scale)(scalingLevel, scalingLevel, center.x, center.y);
    return (0, _transform.compose)([translationMatrix, scalingMatrix, rotationMatrix]);
  }
});

// ../../../../tools/circuit-to-wokwi/node_modules/transformation-matrix/build-commonjs/index.js
var require_build_commonjs = __commonJS(function(exports) {
  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  var _applyToPoint = require_applyToPoint();
  Object.keys(_applyToPoint).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _applyToPoint[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _applyToPoint[key];
      }
    });
  });
  var _fromObject = require_fromObject();
  Object.keys(_fromObject).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _fromObject[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _fromObject[key];
      }
    });
  });
  var _fromString = require_fromString();
  Object.keys(_fromString).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _fromString[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _fromString[key];
      }
    });
  });
  var _identity = require_identity();
  Object.keys(_identity).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _identity[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _identity[key];
      }
    });
  });
  var _inverse = require_inverse();
  Object.keys(_inverse).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _inverse[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _inverse[key];
      }
    });
  });
  var _isAffineMatrix = require_isAffineMatrix();
  Object.keys(_isAffineMatrix).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _isAffineMatrix[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _isAffineMatrix[key];
      }
    });
  });
  var _rotate = require_rotate();
  Object.keys(_rotate).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _rotate[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _rotate[key];
      }
    });
  });
  var _scale = require_scale();
  Object.keys(_scale).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _scale[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _scale[key];
      }
    });
  });
  var _shear = require_shear();
  Object.keys(_shear).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _shear[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _shear[key];
      }
    });
  });
  var _skew = require_skew();
  Object.keys(_skew).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _skew[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _skew[key];
      }
    });
  });
  var _toString = require_toString();
  Object.keys(_toString).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _toString[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _toString[key];
      }
    });
  });
  var _transform = require_transform();
  Object.keys(_transform).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _transform[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _transform[key];
      }
    });
  });
  var _translate = require_translate();
  Object.keys(_translate).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _translate[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _translate[key];
      }
    });
  });
  var _fromTriangles = require_fromTriangles();
  Object.keys(_fromTriangles).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _fromTriangles[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _fromTriangles[key];
      }
    });
  });
  var _smoothMatrix = require_smoothMatrix();
  Object.keys(_smoothMatrix).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _smoothMatrix[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _smoothMatrix[key];
      }
    });
  });
  var _fromDefinition = require_fromDefinition();
  Object.keys(_fromDefinition).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _fromDefinition[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _fromDefinition[key];
      }
    });
  });
  var _fromTransformAttribute = require_fromTransformAttribute();
  Object.keys(_fromTransformAttribute).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _fromTransformAttribute[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _fromTransformAttribute[key];
      }
    });
  });
  var _decompose = require_decompose();
  Object.keys(_decompose).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _decompose[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _decompose[key];
      }
    });
  });
  var _flip = require_flip();
  Object.keys(_flip).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _flip[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _flip[key];
      }
    });
  });
  var _fromMovingPoints = require_fromMovingPoints();
  Object.keys(_fromMovingPoints).forEach(function(key) {
    if (key === "default" || key === "__esModule")
      return;
    if (key in exports && exports[key] === _fromMovingPoints[key])
      return;
    Object.defineProperty(exports, key, {
      enumerable: true,
      get: function() {
        return _fromMovingPoints[key];
      }
    });
  });
});

// cli.ts
import { readFile, writeFile } from "node:fs/promises";

// lib/geometry.ts
import { readdirSync, readFileSync as readFileSync2 } from "node:fs";
import { join } from "node:path";

// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/registry/parts.json
var parts_default = [
  {
    type: "board-aitewinrobot-esp32c3-supermini",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "3V3",
      "4",
      "5",
      "5V",
      "6",
      "7",
      "8",
      "9",
      "10",
      "GND",
      "RX",
      "TX"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-aitewinrobot-esp32h2-supermini",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "3V3",
      "4",
      "5",
      "5V",
      "8",
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "22",
      "25",
      "26",
      "27",
      "GND",
      "RX",
      "TX"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-arduino-nano-esp32",
    pins: [
      "3V3",
      "$gpio45",
      "A0",
      "A1",
      "A2",
      "A3",
      "A4",
      "A5",
      "A6",
      "A7",
      "B0",
      "B1",
      "D10",
      "D11",
      "D12",
      "D13",
      "D2",
      "D3",
      "D4",
      "D5",
      "D6",
      "D7",
      "D8",
      "D9",
      "GND.1",
      "GND.2",
      "RST",
      "RX0",
      "TX1",
      "VBUS",
      "VIN"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-cd74hc4067",
    pins: [
      "COM",
      "EN",
      "GND",
      "I0",
      "I1",
      "I10",
      "I11",
      "I12",
      "I13",
      "I14",
      "I15",
      "I2",
      "I3",
      "I4",
      "I5",
      "I6",
      "I7",
      "I8",
      "I9",
      "S0",
      "S1",
      "S2",
      "S3",
      "VCC"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-ds18b20",
    pins: [
      "DQ",
      "GND",
      "VCC"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-epaper-2in9",
    pins: [
      "BUSY",
      "CLK",
      "CS",
      "DC",
      "DIN",
      "GND",
      "RST",
      "VCC"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp-01",
    pins: [
      "CH_PD",
      "GND",
      "GPIO0",
      "GPIO2",
      "RESET",
      "RX",
      "TX",
      "VCC"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp32-c3-devkitm-1",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "3V3.1",
      "3V3.2",
      "4",
      "5",
      "5V.1",
      "5V.2",
      "6",
      "7",
      "8",
      "9",
      "10",
      "18",
      "19",
      "GND.1",
      "GND.10",
      "GND.2",
      "GND.3",
      "GND.4",
      "GND.5",
      "GND.6",
      "GND.7",
      "GND.8",
      "GND.9",
      "RST",
      "RX",
      "TX"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp32-c3-rust-1",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "3V3",
      "4",
      "5",
      "5V",
      "6",
      "7",
      "8.1",
      "8.2",
      "9",
      "10",
      "18",
      "19",
      "20",
      "21",
      "$sens1_SCL",
      "$sens1_SDA",
      "$sens2_SCL",
      "$sens2_SDA",
      "BAT+",
      "EN",
      "GND",
      "NC1",
      "NC2",
      "NC3",
      "NC4",
      "NC5",
      "NC6",
      "RST"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp32-c5-devkitc-1",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "3V3",
      "4",
      "5",
      "5V",
      "6",
      "7",
      "8",
      "9",
      "10",
      "13",
      "14",
      "15",
      "23",
      "24",
      "25",
      "26",
      "27",
      "28",
      "GND.1",
      "GND.2",
      "GND.3",
      "GND.4",
      "NC0",
      "NC1",
      "NC2",
      "RST",
      "RX",
      "TX"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp32-c6-devkitc-1",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "3V3",
      "4",
      "5",
      "5V",
      "6",
      "7",
      "8",
      "9",
      "10",
      "11",
      "12",
      "13",
      "15",
      "18",
      "19",
      "20",
      "21",
      "22",
      "23",
      "GND.1",
      "GND.2",
      "GND.3",
      "GND.4",
      "NC0",
      "NC1",
      "RST",
      "RX",
      "TX"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp32-cam",
    pins: [
      "0",
      "2",
      "3V3",
      "4",
      "5V.1",
      "12",
      "13",
      "14",
      "15",
      "16",
      "$gpio33",
      "$gpio4",
      "$sd_clk",
      "$sd_cmd",
      "$sd_d0",
      "$sd_d1",
      "$sd_d2",
      "$sd_d3",
      "GND.1",
      "GND.2",
      "GNd.3",
      "RX",
      "TX",
      "VCC"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp32-devkit-c-v4",
    pins: [
      "0",
      "2",
      "3V3",
      "4",
      "5",
      "5V",
      "12",
      "13",
      "14",
      "15",
      "16",
      "17",
      "18",
      "19",
      "21",
      "22",
      "23",
      "25",
      "26",
      "27",
      "32",
      "33",
      "34",
      "35",
      "CLK",
      "CMD",
      "D0",
      "D1",
      "D2",
      "D3",
      "EN",
      "GND.1",
      "GND.2",
      "GND.3",
      "RX",
      "TX",
      "VN",
      "VP"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp32-devkit-v1",
    pins: [
      "3V3",
      "D12",
      "D13",
      "D14",
      "D15",
      "D18",
      "D19",
      "D2",
      "D21",
      "D22",
      "D23",
      "D25",
      "D26",
      "D27",
      "D32",
      "D33",
      "D34",
      "D35",
      "D4",
      "D5",
      "EN",
      "GND.1",
      "GND.2",
      "RX0",
      "RX2",
      "TX0",
      "TX2",
      "VIN",
      "VN",
      "VP"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp32-h2-devkitm-1",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "3V3",
      "4",
      "5",
      "5V",
      "8",
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "22",
      "25",
      "26",
      "27",
      "GND.1",
      "GND.2",
      "GND.3",
      "GND.4",
      "GND.5",
      "GND.6",
      "NC",
      "RST",
      "RX",
      "TX",
      "VBAT"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp32-p4-function-ev",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "3V3.1",
      "3V3.2",
      "4",
      "5",
      "5V.1",
      "5V.2",
      "6",
      "7",
      "8",
      "20",
      "21",
      "22",
      "23",
      "24",
      "25",
      "26",
      "27",
      "32",
      "33",
      "36",
      "37",
      "38",
      "45",
      "46",
      "47",
      "48",
      "53",
      "54",
      "$gpio10",
      "$gpio11",
      "$gpio12",
      "$gpio13",
      "$gpio14",
      "$gpio15",
      "$gpio16",
      "$gpio17",
      "$gpio18",
      "$gpio19",
      "$gpio28",
      "$gpio29",
      "$gpio30",
      "$gpio31",
      "$gpio34",
      "$gpio35",
      "$gpio39",
      "$gpio40",
      "$gpio41",
      "$gpio42",
      "$gpio43",
      "$gpio44",
      "$gpio49",
      "$gpio50",
      "$gpio51",
      "$gpio52",
      "$gpio9",
      "GND.1",
      "GND.2",
      "GND.3",
      "GND.4",
      "GND.5",
      "GND.6",
      "GND.7",
      "GND.8"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp32-p4-preview",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "3V3",
      "4",
      "5",
      "5V",
      "6",
      "7",
      "8",
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15",
      "16",
      "17",
      "18",
      "19",
      "20",
      "21",
      "22",
      "23",
      "24",
      "25",
      "26",
      "27",
      "28",
      "29",
      "30",
      "31",
      "32",
      "33",
      "34",
      "35",
      "36",
      "39",
      "40",
      "41",
      "42",
      "43",
      "44",
      "45",
      "46",
      "47",
      "48",
      "49",
      "50",
      "51",
      "52",
      "53",
      "54",
      "55",
      "GND.1",
      "GND.2",
      "GND.3",
      "RST",
      "RX",
      "TX"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp32-s2-devkitm-1",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "3V3",
      "4",
      "5",
      "5V",
      "6",
      "7",
      "8",
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15",
      "16",
      "17",
      "18",
      "19",
      "20",
      "21",
      "26",
      "33",
      "34",
      "35",
      "36",
      "37",
      "38",
      "39",
      "40",
      "41",
      "42",
      "45",
      "46",
      "GND.1",
      "GND.2",
      "RST",
      "RX",
      "TX"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp32-s3-box-3",
    pins: [
      "3V3.1",
      "3V3.2",
      "3V3.3",
      "3V3.4",
      "$gpio18",
      "$gpio3",
      "$gpio4",
      "$gpio48",
      "$gpio5",
      "$gpio6",
      "$gpio7",
      "$gpio8",
      "G10",
      "G11",
      "G12",
      "G13",
      "G14",
      "G19",
      "G20",
      "G21",
      "G38",
      "G39",
      "G40",
      "G41",
      "G42",
      "G43",
      "G44",
      "G9",
      "GND.1",
      "GND.2",
      "GND.3",
      "GND.4"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp32-s3-box",
    pins: [
      "3V3.1",
      "3V3.2",
      "3V3.3",
      "3V3.4",
      "$gpio18",
      "$gpio3",
      "$gpio4",
      "$gpio48",
      "$gpio5",
      "$gpio6",
      "$gpio7",
      "$gpio8",
      "G10",
      "G11",
      "G12",
      "G13",
      "G14",
      "G19",
      "G20",
      "G21",
      "G38",
      "G39",
      "G40",
      "G41",
      "G42",
      "G43",
      "G44",
      "G9",
      "GND.1",
      "GND.2",
      "GND.3",
      "GND.4"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-esp32-s3-devkitc-1",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "3V3.1",
      "3V3.2",
      "4",
      "5",
      "5V",
      "6",
      "7",
      "8",
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15",
      "16",
      "17",
      "18",
      "19",
      "20",
      "21",
      "35",
      "36",
      "37",
      "38",
      "39",
      "40",
      "41",
      "42",
      "45",
      "46",
      "47",
      "48",
      "GND.1",
      "GND.2",
      "GND.3",
      "GND.4",
      "RST",
      "RX",
      "TX"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-franzininho-wifi",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "3V3.1",
      "3V3.2",
      "4",
      "5",
      "5V.1",
      "5V.2",
      "5V.3",
      "6",
      "7",
      "8",
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15",
      "16",
      "17",
      "18",
      "21",
      "21.2",
      "26",
      "33",
      "34",
      "35",
      "36",
      "37",
      "38",
      "39",
      "40",
      "41",
      "42",
      "43",
      "44",
      "45",
      "46",
      "GND.1",
      "GND.2",
      "GND.3",
      "GND.4",
      "GND.5",
      "GND.6",
      "GND.7",
      "SCL",
      "SDA"
    ],
    documented: true,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-grove-oled-sh1107",
    pins: [
      "GND.1",
      "SCL.1",
      "SDA",
      "VCC"
    ],
    documented: true,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-ili9341-cap-touch",
    pins: [
      "CS",
      "D/C",
      "GND",
      "LED",
      "MISO",
      "MOSI",
      "RST",
      "SCK",
      "SCL",
      "SDA",
      "VCC"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-ili9881c-8in",
    pins: [],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-lm35",
    pins: [
      "GND",
      "OUT",
      "VCC"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-m5stack-core-s3",
    pins: [
      "3V3.1",
      "5V.1",
      "$gpio3",
      "$gpio35",
      "$gpio36",
      "$gpio37",
      "BAT",
      "G0",
      "G1",
      "G10",
      "G11",
      "G12",
      "G13",
      "G14",
      "G17",
      "G18",
      "G2",
      "G35",
      "G36",
      "G37",
      "G43",
      "G44",
      "G5",
      "G6",
      "G7",
      "G8",
      "G8.2",
      "G9",
      "G9.2",
      "GND.1",
      "GND.2",
      "GND.3",
      "GND.4",
      "GND.5",
      "GND.6",
      "RST.1",
      "RX",
      "SCL",
      "SDA",
      "TX",
      "VCC.1",
      "VCC.2",
      "VCC.3"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-mch2022-badge",
    pins: [
      "3V3",
      "$kite1",
      "$kite2",
      "$kite3",
      "$kite4",
      "D12",
      "D13",
      "D14",
      "D15",
      "D18",
      "D19",
      "D2",
      "D21",
      "D22",
      "D23",
      "D25",
      "D26",
      "D27",
      "D32",
      "D33",
      "D34",
      "D35",
      "D4",
      "D5",
      "EN",
      "GND",
      "RX0",
      "RX2",
      "TX0",
      "TX2",
      "VIN",
      "VN",
      "VP"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-nokia-5110",
    pins: [
      "BL",
      "BL.2",
      "CE",
      "CE.2",
      "CLK",
      "CLK.2 ",
      "DC",
      "DC.2",
      "DIN",
      "DIN.2 ",
      "GND",
      "GND.2 ",
      "RST",
      "RST.2 ",
      "VCC",
      "VCC.2 "
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-notecarrier-a",
    pins: [
      "ATTN",
      "AUX1",
      "AUX2",
      "AUX3",
      "AUX4",
      "AUXEN",
      "AUXRX",
      "AUXTX",
      "BAT",
      "EN",
      "GND",
      "MAIN",
      "NC1",
      "NC2",
      "RST",
      "RX",
      "SCL",
      "SDA",
      "TX",
      "V+",
      "VIO",
      "VUSB"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-pi-pico-w",
    pins: [
      "3V3",
      "3V3_EN",
      "$gpio24",
      "$gpio29",
      "ADC_VREF",
      "GND.1",
      "GND.2",
      "GND.3",
      "GND.4",
      "GND.5",
      "GND.6",
      "GND.7",
      "GND.8",
      "GP0",
      "GP1",
      "GP10",
      "GP11",
      "GP12",
      "GP13",
      "GP14",
      "GP15",
      "GP16",
      "GP17",
      "GP18",
      "GP19",
      "GP2",
      "GP20",
      "GP21",
      "GP22",
      "GP26",
      "GP27",
      "GP28",
      "GP3",
      "GP4",
      "GP5",
      "GP6",
      "GP7",
      "GP8",
      "GP9",
      "RUN",
      "TP4",
      "TP5",
      "VBUS",
      "VSYS"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-pi-pico",
    pins: [
      "3V3",
      "3V3_EN",
      "ADC_VREF",
      "GND.1",
      "GND.2",
      "GND.3",
      "GND.4",
      "GND.5",
      "GND.6",
      "GND.7",
      "GND.8",
      "GP0",
      "GP1",
      "GP10",
      "GP11",
      "GP12",
      "GP13",
      "GP14",
      "GP15",
      "GP16",
      "GP17",
      "GP18",
      "GP19",
      "GP2",
      "GP20",
      "GP21",
      "GP22",
      "GP26",
      "GP27",
      "GP28",
      "GP3",
      "GP4",
      "GP5",
      "GP6",
      "GP7",
      "GP8",
      "GP9",
      "RUN",
      "TP4",
      "TP5",
      "VBUS",
      "VSYS"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-ssd1306",
    pins: [
      "GND",
      "SCL",
      "SDA",
      "VCC"
    ],
    documented: true,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-st-nucleo-c031c6",
    pins: [
      "3V3.1",
      "3V3.2",
      "5V.1",
      "5V.2",
      "5V.3",
      "A0",
      "A1",
      "A2",
      "A3",
      "A4",
      "A5",
      "AGND",
      "AVDD.1",
      "AVDD.2",
      "D0",
      "D1",
      "D10",
      "D11",
      "D12",
      "D13",
      "D14",
      "D15",
      "D2",
      "D3",
      "D4",
      "D5",
      "D6",
      "D7",
      "D8",
      "D9",
      "E5V",
      "GND.1",
      "GND.2",
      "GND.3",
      "GND.4",
      "GND.5",
      "GND.6",
      "GND.7",
      "GND.8",
      "GND.9",
      "IOREF.1",
      "IOREF.2",
      "NRST.1",
      "NRST.2",
      "PA0",
      "PA1",
      "PA10",
      "PA11",
      "PA12",
      "PA13",
      "PA14",
      "PA15",
      "PA2",
      "PA3",
      "PA4",
      "PA5",
      "PA6",
      "PA7",
      "PA8",
      "PA9",
      "PB0.1",
      "PB0.2",
      "PB1",
      "PB10",
      "PB11",
      "PB12.1",
      "PB12.2",
      "PB13",
      "PB14",
      "PB15",
      "PB2",
      "PB3",
      "PB4",
      "PB5",
      "PB6",
      "PB7",
      "PB8",
      "PB9",
      "PC13",
      "PC14",
      "PC15",
      "PC6",
      "PC7",
      "PD0",
      "PD1",
      "PD2",
      "PD2.2",
      "PD3",
      "PF0",
      "PF1",
      "PF3",
      "VDD",
      "VIN.1",
      "VIN.2"
    ],
    documented: true,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-st-nucleo-l031k6",
    pins: [
      "3V3",
      "5V",
      "A0",
      "A1",
      "A2",
      "A3",
      "A4",
      "A5",
      "A6",
      "A7",
      "D0",
      "D1",
      "D10",
      "D11",
      "D12",
      "D13",
      "D2",
      "D3",
      "D4",
      "D5",
      "D6",
      "D7",
      "D8",
      "D9",
      "GND.1",
      "GND.2",
      "REF",
      "RST.1",
      "RST.2",
      "VCP_RX",
      "VCP_TX",
      "VIN"
    ],
    documented: true,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-st-nucleo-l432kc",
    pins: [
      "3V3",
      "5V",
      "A0",
      "A1",
      "A2",
      "A3",
      "A4",
      "A5",
      "A6",
      "A7",
      "D0",
      "D1",
      "D10",
      "D11",
      "D12",
      "D13",
      "D2",
      "D3",
      "D4",
      "D5",
      "D6",
      "D7",
      "D8",
      "D9",
      "GND.1",
      "GND.2",
      "REF",
      "RST.1",
      "RST.2",
      "VCP_RX",
      "VCP_TX",
      "VIN"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-st7789",
    pins: [
      "BL",
      "CS",
      "DC",
      "GND",
      "RST",
      "SCL",
      "SDA",
      "VCC"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-stm32-blackpill",
    pins: [
      "3V3.1",
      "3V3.2",
      "5V.1",
      "5V.2",
      "A0",
      "A1",
      "A10",
      "A11",
      "A12",
      "A15",
      "A2",
      "A3",
      "A4",
      "A5",
      "A6",
      "A7",
      "A8",
      "A9",
      "B0",
      "B1",
      "B10",
      "B12",
      "B13",
      "B14",
      "B15",
      "B2",
      "B3",
      "B4",
      "B5",
      "B6",
      "B7",
      "B8",
      "B9",
      "C13",
      "C14",
      "C15",
      "GND.1",
      "GND.3",
      "led",
      "R",
      "VB"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-stm32-bluepill",
    pins: [
      "3V3.1",
      "3V3.2",
      "5V.1",
      "A0",
      "A1",
      "A10",
      "A11",
      "A12",
      "A15",
      "A2",
      "A3",
      "A4",
      "A5",
      "A6",
      "A7",
      "A8",
      "A9",
      "B0",
      "B1",
      "B10",
      "B11",
      "B12",
      "B13",
      "B14",
      "B15",
      "B3",
      "B4",
      "B5",
      "B6",
      "B7",
      "B8",
      "B9",
      "C13",
      "C14",
      "C15",
      "GND.1",
      "GND.2",
      "GND.3",
      "R",
      "VBAT"
    ],
    documented: true,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-tt-block-bidirectional-io",
    pins: [
      "IN",
      "OE",
      "OUT",
      "UIO"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-tt-block-input-8",
    pins: [
      "EXTIN0",
      "EXTIN1",
      "EXTIN2",
      "EXTIN3",
      "EXTIN4",
      "EXTIN5",
      "EXTIN6",
      "EXTIN7",
      "IN0",
      "IN1",
      "IN2",
      "IN3",
      "IN4",
      "IN5",
      "IN6",
      "IN7"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-tt-block-input",
    pins: [
      "CLK",
      "EXTCLK",
      "EXTIN0",
      "EXTIN1",
      "EXTIN2",
      "EXTIN3",
      "EXTIN4",
      "EXTIN5",
      "EXTIN6",
      "EXTIN7",
      "EXTRST_N",
      "IN0",
      "IN1",
      "IN2",
      "IN3",
      "IN4",
      "IN5",
      "IN6",
      "IN7",
      "RST_N"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-tt-block-output",
    pins: [
      "EXTOUT0",
      "EXTOUT1",
      "EXTOUT2",
      "EXTOUT3",
      "EXTOUT4",
      "EXTOUT5",
      "EXTOUT6",
      "EXTOUT7",
      "OUT0",
      "OUT1",
      "OUT2",
      "OUT3",
      "OUT4",
      "OUT5",
      "OUT6",
      "OUT7"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-wemos-lolin32-lite",
    pins: [
      "3V",
      "BAT-",
      "BAT+",
      "EN",
      "GND",
      "GPIO0",
      "GPIO12",
      "GPIO13",
      "GPIO14",
      "GPIO15",
      "GPIO16",
      "GPIO17",
      "GPIO18",
      "GPIO19",
      "GPIO2",
      "GPIO22",
      "GPIO23",
      "GPIO25",
      "GPIO26",
      "GPIO27",
      "GPIO32",
      "GPIO33",
      "GPIO34",
      "GPIO35",
      "GPIO4",
      "GPIO5",
      "RX",
      "TX",
      "VN",
      "VP"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-wemos-s2-mini",
    pins: [
      "1",
      "2",
      "3",
      "3V3",
      "4",
      "5",
      "6",
      "7(SCK)",
      "8",
      "9(MISO)",
      "10",
      "11(MOSI)",
      "12",
      "13",
      "14",
      "15",
      "16",
      "17",
      "18",
      "21",
      "33(SDA)",
      "34",
      "35(SCL)",
      "36",
      "37",
      "38",
      "39",
      "40",
      "EN",
      "GND.1",
      "GND.2",
      "VBUS"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-xiao-esp32-c3",
    pins: [
      "3V3",
      "5V",
      "D0",
      "D1",
      "D10",
      "D2",
      "D3",
      "D4",
      "D5",
      "D6",
      "D7",
      "D8",
      "D9",
      "GND"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-xiao-esp32-c6",
    pins: [
      "3V3",
      "5V",
      "$gpio15",
      "D0",
      "D1",
      "D10",
      "D2",
      "D3",
      "D4",
      "D5",
      "D6",
      "D7",
      "D8",
      "D9",
      "GND"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "board-xiao-esp32-s3",
    pins: [
      "3V3",
      "5V",
      "$gpio21",
      "D0",
      "D1",
      "D10",
      "D2",
      "D3",
      "D4",
      "D5",
      "D6",
      "D7",
      "D8",
      "D9",
      "GND"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "wokwi-74hc165",
    pins: [
      "PL",
      "CP",
      "D4",
      "D5",
      "D6",
      "D7",
      "Q7_N",
      "GND",
      "Q7",
      "DS",
      "D0",
      "D1",
      "D2",
      "D3",
      "CE",
      "VCC"
    ],
    documented: true,
    category: "logic"
  },
  {
    type: "wokwi-74hc595",
    pins: [
      "Q1",
      "Q2",
      "Q3",
      "Q4",
      "Q5",
      "Q6",
      "Q7",
      "GND",
      "Q7S",
      "MR",
      "SHCP",
      "STCP",
      "OE",
      "DS",
      "Q0",
      "VCC"
    ],
    documented: true,
    category: "logic"
  },
  {
    type: "wokwi-7segment",
    pins: [
      "A",
      "B",
      "C",
      "D",
      "E",
      "F",
      "G",
      "DP",
      "DIG1",
      "DIG2",
      "DIG3",
      "DIG4",
      "COM",
      "COM.1",
      "COM.2",
      "CLN"
    ],
    attrs: [
      {
        name: "color",
        type: "string"
      },
      {
        name: "colon",
        type: "string"
      },
      {
        name: "common",
        type: "string",
        validValues: [
          "anode",
          "cathode"
        ]
      },
      {
        name: "digits",
        type: "string"
      }
    ],
    documented: true,
    category: "displays"
  },
  {
    type: "wokwi-a4988",
    pins: [
      "ENABLE",
      "MS1",
      "MS2",
      "MS3",
      "RESET",
      "SLEEP",
      "STEP",
      "DIR",
      "GND",
      "GND.1",
      "GND.2",
      "VDD",
      "1B",
      "1A",
      "2A",
      "2B",
      "VMOT"
    ],
    documented: true,
    category: "motors"
  },
  {
    type: "wokwi-analog-joystick",
    pins: [
      "VCC",
      "VERT",
      "HORZ",
      "SEL",
      "GND"
    ],
    attrs: [
      {
        name: "bounce",
        type: "string"
      }
    ],
    documented: true,
    category: "input"
  },
  {
    type: "wokwi-apa102-matrix",
    pins: [
      "DI",
      "CI",
      "VCC",
      "GND",
      "DO",
      "CO"
    ],
    attrs: [
      {
        name: "rows",
        type: "number"
      },
      {
        name: "cols",
        type: "number"
      },
      {
        name: "matrixLayout",
        type: "string"
      },
      {
        name: "matrixBrightness",
        type: "number"
      }
    ],
    documented: false,
    category: "leds"
  },
  {
    type: "wokwi-arduino-mega",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "4",
      "5",
      "6",
      "7",
      "8",
      "9",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15",
      "16",
      "17",
      "18",
      "19",
      "20",
      "21",
      "22",
      "23",
      "24",
      "25",
      "26",
      "27",
      "28",
      "29",
      "30",
      "31",
      "32",
      "33",
      "34",
      "35",
      "36",
      "37",
      "38",
      "39",
      "40",
      "41",
      "42",
      "43",
      "44",
      "45",
      "46",
      "47",
      "48",
      "49",
      "50",
      "51",
      "52",
      "53",
      "GND",
      "GND.1",
      "GND.2",
      "GND.3",
      "GND.4",
      "GND.5",
      "5V",
      "5V.1",
      "5V.2",
      "3.3V",
      "VIN",
      "IOREF",
      "RESET",
      "SCL",
      "SDA",
      "A0",
      "A1",
      "A2",
      "A3",
      "A4",
      "A5",
      "A6",
      "A7",
      "A8",
      "A9",
      "A10",
      "A11",
      "A12",
      "A13",
      "A14",
      "A15",
      "AREF"
    ],
    documented: true,
    isBoard: true,
    category: "boards"
  },
  {
    type: "wokwi-arduino-nano",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "4",
      "5",
      "6",
      "7",
      "8",
      "9",
      "10",
      "11",
      "12",
      "13",
      "GND",
      "GND.1",
      "GND.2",
      "GND.3",
      "5V",
      "5V.2",
      "3.3V",
      "VIN",
      "RESET",
      "RESET.2",
      "RESET.3",
      "A0",
      "A1",
      "A2",
      "A3",
      "A4",
      "A5",
      "A6",
      "A7",
      "AREF",
      "11.2",
      "12.2",
      "13.2"
    ],
    documented: true,
    isBoard: true,
    category: "boards"
  },
  {
    type: "wokwi-arduino-uno",
    pins: [
      "0",
      "1",
      "2",
      "3",
      "4",
      "5",
      "6",
      "7",
      "8",
      "9",
      "10",
      "11",
      "12",
      "13",
      "GND",
      "GND.1",
      "GND.2",
      "GND.3",
      "5V",
      "3.3V",
      "VIN",
      "IOREF",
      "RESET",
      "A0",
      "A1",
      "A2",
      "A3",
      "A4",
      "A4.2",
      "A5",
      "A5.2",
      "AREF"
    ],
    documented: true,
    isBoard: true,
    category: "boards"
  },
  {
    type: "wokwi-attiny85",
    pins: [
      "PB0",
      "PB1",
      "PB2",
      "PB3",
      "PB4",
      "PB5",
      "GND",
      "VCC",
      "RST"
    ],
    documented: true,
    isBoard: true,
    category: "boards"
  },
  {
    type: "wokwi-biaxial-stepper",
    pins: [
      "A1-",
      "A1+",
      "B1+",
      "B1-",
      "A2-",
      "A2+",
      "B2+",
      "B2-"
    ],
    attrs: [
      {
        name: "innerHand",
        type: "string"
      },
      {
        name: "outerHand",
        type: "string"
      }
    ],
    documented: true,
    category: "motors"
  },
  {
    type: "wokwi-breadboard-half",
    pins: [],
    attrs: [],
    documented: true,
    category: "wiring"
  },
  {
    type: "wokwi-breadboard-mini",
    pins: [],
    attrs: [],
    documented: true,
    category: "wiring"
  },
  {
    type: "wokwi-breadboard",
    pins: [],
    attrs: [],
    documented: true,
    category: "wiring"
  },
  {
    type: "wokwi-buzzer",
    pins: [
      "1",
      "2"
    ],
    attrs: [
      {
        name: "volume",
        type: "number"
      },
      {
        name: "mode",
        type: "string",
        validValues: [
          "smooth",
          "accurate"
        ]
      }
    ],
    documented: true,
    category: "passive"
  },
  {
    type: "wokwi-clock-generator",
    pins: [
      "CLK",
      "GND"
    ],
    attrs: [
      {
        name: "frequency",
        type: "number"
      }
    ],
    documented: false,
    category: "timing"
  },
  {
    type: "wokwi-dht22",
    pins: [
      "VCC",
      "SDA",
      "NC",
      "GND"
    ],
    attrs: [
      {
        name: "temperature",
        type: "number"
      },
      {
        name: "humidity",
        type: "number"
      }
    ],
    documented: true,
    category: "sensors"
  },
  {
    type: "wokwi-dip-switch-8",
    pins: [
      "1a",
      "1b",
      "2a",
      "2b",
      "3a",
      "3b",
      "4a",
      "4b",
      "5a",
      "5b",
      "6a",
      "6b",
      "7a",
      "7b",
      "8a",
      "8b"
    ],
    documented: true,
    category: "input"
  },
  {
    type: "wokwi-ds1307",
    pins: [
      "GND",
      "5V",
      "SDA",
      "SCL",
      "SQW"
    ],
    attrs: [
      {
        name: "initTime",
        type: "string"
      }
    ],
    documented: true,
    category: "timing"
  },
  {
    type: "wokwi-ds18b20",
    pins: [
      "VCC",
      "DQ",
      "GND"
    ],
    attrs: [
      {
        name: "temperature",
        type: "number"
      },
      {
        name: "familyCode",
        type: "string"
      },
      {
        name: "deviceID",
        type: "string"
      }
    ],
    documented: false,
    category: "sensors"
  },
  {
    type: "wokwi-esp32-devkit-v1",
    pins: [
      "VIN",
      "GND.1",
      "GND.2",
      "D2",
      "D4",
      "D5",
      "D12",
      "D13",
      "D14",
      "D15",
      "D18",
      "D19",
      "D21",
      "D22",
      "D23",
      "D25",
      "D26",
      "D27",
      "D32",
      "D33",
      "D34",
      "D35",
      "VN",
      "VP",
      "EN",
      "TX0",
      "TX2",
      "RX0",
      "RX2",
      "3V3"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "wokwi-flip-flop-d",
    pins: [
      "D",
      "CLK",
      "Q",
      "NOTQ",
      "S",
      "R"
    ],
    documented: false,
    category: "logic"
  },
  {
    type: "wokwi-flip-flop-dr",
    pins: [
      "D",
      "CLK",
      "Q",
      "NOTQ",
      "S",
      "R"
    ],
    documented: false,
    category: "logic"
  },
  {
    type: "wokwi-flip-flop-dsr",
    pins: [
      "D",
      "CLK",
      "Q",
      "NOTQ",
      "S",
      "R"
    ],
    documented: false,
    category: "logic"
  },
  {
    type: "wokwi-flip-flop-sr",
    pins: [
      "S",
      "CLK",
      "R",
      "Q",
      "NOTQ"
    ],
    documented: false,
    category: "logic"
  },
  {
    type: "wokwi-franzininho",
    pins: [
      "GND.1",
      "VCC.1",
      "PB4",
      "PB5",
      "PB3",
      "PB2",
      "PB1",
      "PB0",
      "VIN",
      "GND.2",
      "VCC.2"
    ],
    documented: true,
    isBoard: true,
    category: "boards"
  },
  {
    type: "wokwi-gas-sensor",
    pins: [
      "VCC",
      "GND",
      "DOUT",
      "AOUT"
    ],
    attrs: [
      {
        name: "ppm",
        type: "number"
      },
      {
        name: "threshold",
        type: "number"
      }
    ],
    documented: true,
    category: "sensors"
  },
  {
    type: "wokwi-gate-and-2",
    pins: [
      "A",
      "B",
      "OUT"
    ],
    documented: false,
    category: "logic"
  },
  {
    type: "wokwi-gate-buffer",
    pins: [
      "IN",
      "OUT"
    ],
    documented: false,
    category: "logic"
  },
  {
    type: "wokwi-gate-nand-2",
    pins: [
      "A",
      "B",
      "OUT"
    ],
    documented: false,
    category: "logic"
  },
  {
    type: "wokwi-gate-nor-2",
    pins: [
      "A",
      "B",
      "OUT"
    ],
    documented: false,
    category: "logic"
  },
  {
    type: "wokwi-gate-not",
    pins: [
      "IN",
      "OUT"
    ],
    documented: false,
    category: "logic"
  },
  {
    type: "wokwi-gate-or-2",
    pins: [
      "A",
      "B",
      "OUT"
    ],
    documented: false,
    category: "logic"
  },
  {
    type: "wokwi-gate-xnor-2",
    pins: [
      "A",
      "B",
      "OUT"
    ],
    documented: false,
    category: "logic"
  },
  {
    type: "wokwi-gate-xor-2",
    pins: [
      "A",
      "B",
      "OUT"
    ],
    documented: false,
    category: "logic"
  },
  {
    type: "wokwi-gnd",
    pins: [
      "GND"
    ],
    documented: false,
    category: "power"
  },
  {
    type: "wokwi-hc-sr04",
    pins: [
      "VCC",
      "TRIG",
      "ECHO",
      "GND"
    ],
    attrs: [
      {
        name: "distance",
        type: "number"
      }
    ],
    documented: true,
    category: "sensors"
  },
  {
    type: "wokwi-hub75-matrix",
    pins: [
      "R1",
      "G1",
      "B1",
      "R2",
      "G2",
      "B2",
      "A",
      "B",
      "C",
      "D",
      "E",
      "CLK",
      "LAT",
      "OE",
      "GND"
    ],
    attrs: [
      {
        name: "rows",
        type: "number"
      },
      {
        name: "cols",
        type: "number"
      }
    ],
    documented: false,
    category: "displays"
  },
  {
    type: "wokwi-hx711",
    pins: [
      "GND",
      "DT",
      "SCK",
      "VCC"
    ],
    attrs: [
      {
        name: "type",
        type: "string",
        validValues: [
          "50kg",
          "5kg",
          "gauge"
        ]
      },
      {
        name: "weight",
        type: "number"
      }
    ],
    documented: true,
    category: "sensors"
  },
  {
    type: "wokwi-il9163",
    pins: [
      "D/C",
      "CS",
      "SDA",
      "SCL",
      "RST",
      "LED",
      "VCC",
      "GND"
    ],
    documented: false,
    category: "displays"
  },
  {
    type: "wokwi-ili9341",
    pins: [
      "D/C",
      "CS",
      "SCK",
      "MOSI",
      "MISO",
      "RST",
      "LED",
      "VCC",
      "GND"
    ],
    attrs: [
      {
        name: "flipHorizontal",
        type: "boolean"
      },
      {
        name: "flipVertical",
        type: "boolean"
      },
      {
        name: "swapXY",
        type: "boolean"
      }
    ],
    documented: true,
    category: "displays"
  },
  {
    type: "wokwi-ir-receiver",
    pins: [
      "VCC",
      "DAT",
      "GND"
    ],
    documented: true,
    category: "communication"
  },
  {
    type: "wokwi-ir-remote",
    pins: [],
    attrs: [
      {
        name: "key",
        type: "string"
      }
    ],
    documented: true,
    category: "communication"
  },
  {
    type: "wokwi-ks2e-m-dc5",
    pins: [
      "COIL1",
      "COIL2",
      "P1",
      "NO1",
      "NC1",
      "P2",
      "NO2",
      "NC2"
    ],
    attrs: [
      {
        name: "bounce",
        type: "string"
      }
    ],
    documented: true,
    category: "motors"
  },
  {
    type: "wokwi-ky-040",
    pins: [
      "CLK",
      "DT",
      "SW",
      "VCC",
      "GND"
    ],
    documented: true,
    category: "input"
  },
  {
    type: "wokwi-lcd1602",
    pins: [
      "A",
      "K",
      "V0",
      "RS",
      "RW",
      "E",
      "D0",
      "D1",
      "D2",
      "D3",
      "D4",
      "D5",
      "D6",
      "D7",
      "VSS",
      "VDD",
      "GND",
      "VCC",
      "SCL",
      "SDA"
    ],
    attrs: [
      {
        name: "i2cAddress",
        type: "string"
      },
      {
        name: "i2c-address",
        type: "string"
      },
      {
        name: "pins",
        type: "string",
        validValues: [
          "full",
          "i2c"
        ]
      },
      {
        name: "variant",
        type: "string"
      },
      {
        name: "color",
        type: "string"
      },
      {
        name: "background",
        type: "string"
      }
    ],
    documented: true,
    category: "displays"
  },
  {
    type: "wokwi-lcd2004",
    pins: [
      "A",
      "K",
      "V0",
      "RS",
      "RW",
      "E",
      "D0",
      "D1",
      "D2",
      "D3",
      "D4",
      "D5",
      "D6",
      "D7",
      "VSS",
      "VDD",
      "GND",
      "VCC",
      "SCL",
      "SDA"
    ],
    attrs: [
      {
        name: "i2cAddress",
        type: "string"
      },
      {
        name: "i2c-address",
        type: "string"
      },
      {
        name: "pins",
        type: "string",
        validValues: [
          "full",
          "i2c"
        ]
      },
      {
        name: "variant",
        type: "string"
      },
      {
        name: "color",
        type: "string"
      },
      {
        name: "background",
        type: "string"
      }
    ],
    documented: true,
    category: "displays"
  },
  {
    type: "wokwi-led-bar-graph",
    pins: [
      "A1",
      "A2",
      "A3",
      "A4",
      "A5",
      "A6",
      "A7",
      "A8",
      "A9",
      "A10",
      "C1",
      "C2",
      "C3",
      "C4",
      "C5",
      "C6",
      "C7",
      "C8",
      "C9",
      "C10"
    ],
    attrs: [
      {
        name: "color",
        type: "string"
      }
    ],
    documented: true,
    category: "leds"
  },
  {
    type: "wokwi-led-matrix",
    pins: [
      "DIN",
      "VDD",
      "VSS",
      "DOUT"
    ],
    attrs: [
      {
        name: "rows",
        type: "number"
      },
      {
        name: "cols",
        type: "number"
      },
      {
        name: "layout",
        type: "string"
      },
      {
        name: "brightness",
        type: "number"
      },
      {
        name: "pixelShape",
        type: "string"
      },
      {
        name: "pixelSize",
        type: "string"
      }
    ],
    documented: true,
    category: "leds"
  },
  {
    type: "wokwi-led-ring",
    pins: [
      "GND",
      "VCC",
      "DIN",
      "DOUT"
    ],
    attrs: [
      {
        name: "pixels",
        type: "number"
      }
    ],
    documented: true,
    category: "leds"
  },
  {
    type: "wokwi-led-strip",
    pins: [
      "VDD",
      "DIN",
      "VSS",
      "VDD.2",
      "DOUT",
      "VSS.2"
    ],
    attrs: [
      {
        name: "pixels",
        type: "number"
      },
      {
        name: "pixelShape",
        type: "string"
      },
      {
        name: "pixelSize",
        type: "string"
      }
    ],
    documented: true,
    category: "leds"
  },
  {
    type: "wokwi-led",
    pins: [
      "A",
      "C"
    ],
    attrs: [
      {
        name: "color",
        type: "string",
        validValues: [
          "red",
          "green",
          "blue",
          "yellow",
          "orange",
          "white",
          "purple",
          "cyan"
        ]
      },
      {
        name: "lightColor",
        type: "string"
      },
      {
        name: "label",
        type: "string"
      },
      {
        name: "gamma",
        type: "number"
      },
      {
        name: "flip",
        type: "string"
      },
      {
        name: "fps",
        type: "number"
      }
    ],
    documented: true,
    category: "leds"
  },
  {
    type: "wokwi-logic-analyzer",
    pins: [
      "D0",
      "D1",
      "D2",
      "D3",
      "D4",
      "D5",
      "D6",
      "D7",
      "GND"
    ],
    attrs: [
      {
        name: "bufferSize",
        type: "number"
      },
      {
        name: "filename",
        type: "string"
      },
      {
        name: "triggerPin",
        type: "string"
      },
      {
        name: "triggerMode",
        type: "string"
      },
      {
        name: "triggerLevel",
        type: "string"
      }
    ],
    documented: true,
    category: "communication"
  },
  {
    type: "wokwi-logo",
    pins: [],
    attrs: [],
    documented: false,
    category: "misc"
  },
  {
    type: "wokwi-max7219-matrix",
    pins: [
      "DIN",
      "DOUT",
      "CS",
      "CS.2",
      "GND",
      "GND.2",
      "V+",
      "V+.2",
      "CLK",
      "CLK.2"
    ],
    attrs: [
      {
        name: "chain",
        type: "number"
      },
      {
        name: "layout",
        type: "string",
        validValues: [
          "parola",
          "fc16"
        ]
      },
      {
        name: "color",
        type: "string"
      }
    ],
    documented: true,
    category: "displays"
  },
  {
    type: "wokwi-membrane-keypad",
    pins: [
      "R1",
      "R2",
      "R3",
      "R4",
      "C1",
      "C2",
      "C3",
      "C4"
    ],
    attrs: [
      {
        name: "columns",
        type: "string",
        validValues: [
          "3",
          "4"
        ]
      },
      {
        name: "keys",
        type: "string"
      }
    ],
    documented: true,
    category: "input"
  },
  {
    type: "wokwi-microphone",
    pins: [
      "1",
      "2"
    ],
    documented: false,
    category: "sensors"
  },
  {
    type: "wokwi-microsd-card",
    pins: [
      "CS",
      "SCK",
      "DI",
      "DO",
      "CD",
      "GND",
      "VCC"
    ],
    documented: true,
    category: "communication"
  },
  {
    type: "wokwi-mpu6050",
    pins: [
      "INT",
      "AD0",
      "XCL",
      "XDA",
      "SDA",
      "SCL",
      "GND",
      "VCC"
    ],
    attrs: [
      {
        name: "accelX",
        type: "number"
      },
      {
        name: "accelY",
        type: "number"
      },
      {
        name: "accelZ",
        type: "number"
      },
      {
        name: "rotationX",
        type: "number"
      },
      {
        name: "rotationY",
        type: "number"
      },
      {
        name: "rotationZ",
        type: "number"
      },
      {
        name: "temperature",
        type: "number"
      }
    ],
    documented: true,
    category: "sensors"
  },
  {
    type: "wokwi-mux-2",
    pins: [
      "A",
      "B",
      "SEL",
      "OUT"
    ],
    documented: false,
    category: "logic"
  },
  {
    type: "wokwi-neopixel-canvas",
    pins: [
      "DIN",
      "VDD",
      "VSS",
      "DOUT"
    ],
    attrs: [
      {
        name: "rows",
        type: "number"
      },
      {
        name: "cols",
        type: "number"
      },
      {
        name: "matrixLayout",
        type: "string"
      },
      {
        name: "matrixBrightness",
        type: "number"
      }
    ],
    documented: false,
    category: "leds"
  },
  {
    type: "wokwi-neopixel-matrix",
    pins: [
      "GND",
      "VCC",
      "DIN",
      "DOUT"
    ],
    attrs: [
      {
        name: "rows",
        type: "number"
      },
      {
        name: "cols",
        type: "number"
      },
      {
        name: "matrixLayout",
        type: "string"
      },
      {
        name: "matrixBrightness",
        type: "number"
      }
    ],
    documented: false,
    category: "leds"
  },
  {
    type: "wokwi-neopixel-meter",
    pins: [
      "DIN"
    ],
    attrs: [
      {
        name: "pixels",
        type: "number"
      }
    ],
    documented: false,
    category: "leds"
  },
  {
    type: "wokwi-neopixel-serial",
    pins: [
      "DIN",
      "VDD",
      "VSS",
      "DOUT"
    ],
    attrs: [
      {
        name: "pixel",
        type: "string"
      },
      {
        name: "pixels",
        type: "number"
      }
    ],
    documented: false,
    category: "leds"
  },
  {
    type: "wokwi-neopixel",
    pins: [
      "DIN",
      "VDD",
      "VSS",
      "DOUT"
    ],
    attrs: [],
    documented: true,
    category: "leds"
  },
  {
    type: "wokwi-nlsf595",
    pins: [
      "QA",
      "QB",
      "QC",
      "QD",
      "QE",
      "QF",
      "QG",
      "QH",
      "GND",
      "SQH",
      "SCLR",
      "SCK",
      "RCK",
      "OE",
      "SI",
      "VCC"
    ],
    documented: true,
    category: "logic"
  },
  {
    type: "wokwi-nokia-5110-screen",
    pins: [
      "RST",
      "CE",
      "DC",
      "DIN",
      "CLK",
      "BL",
      "VCC",
      "GND"
    ],
    documented: true,
    category: "displays"
  },
  {
    type: "wokwi-ntc-temperature-sensor",
    pins: [
      "VCC",
      "OUT",
      "GND"
    ],
    attrs: [
      {
        name: "temperature",
        type: "number"
      },
      {
        name: "beta",
        type: "number"
      }
    ],
    documented: true,
    category: "sensors"
  },
  {
    type: "wokwi-photoresistor-sensor",
    pins: [
      "VCC",
      "GND",
      "DO",
      "AO"
    ],
    attrs: [
      {
        name: "lux",
        type: "number"
      },
      {
        name: "threshold",
        type: "number"
      },
      {
        name: "rl10",
        type: "number"
      },
      {
        name: "gamma",
        type: "number"
      }
    ],
    documented: true,
    category: "sensors"
  },
  {
    type: "wokwi-pi-pico",
    pins: [
      "GP0",
      "GP1",
      "GP2",
      "GP3",
      "GP4",
      "GP5",
      "GP6",
      "GP7",
      "GP8",
      "GP9",
      "GP10",
      "GP11",
      "GP12",
      "GP13",
      "GP14",
      "GP15",
      "GP16",
      "GP17",
      "GP18",
      "GP19",
      "GP20",
      "GP21",
      "GP22",
      "GP26",
      "GP27",
      "GP28",
      "GND.1",
      "GND.2",
      "GND.3",
      "GND.4",
      "GND.5",
      "GND.6",
      "GND.7",
      "GND.8",
      "VBUS",
      "VSYS",
      "3V3_EN",
      "3V3",
      "ADC_VREF",
      "RUN",
      "TP4",
      "TP5"
    ],
    documented: true,
    isBoard: true,
    category: "boards"
  },
  {
    type: "wokwi-pir-motion-sensor",
    pins: [
      "VCC",
      "OUT",
      "GND"
    ],
    attrs: [
      {
        name: "delayTime",
        type: "number"
      },
      {
        name: "inhibitTime",
        type: "number"
      },
      {
        name: "retrigger",
        type: "string",
        validValues: [
          "yes",
          "no"
        ]
      }
    ],
    documented: true,
    category: "sensors"
  },
  {
    type: "wokwi-potentiometer",
    pins: [
      "GND",
      "SIG",
      "VCC"
    ],
    attrs: [
      {
        name: "value",
        type: "number"
      }
    ],
    documented: true,
    category: "input"
  },
  {
    type: "wokwi-pushbutton-6mm",
    pins: [
      "1.l",
      "2.l",
      "1.r",
      "2.r"
    ],
    attrs: [
      {
        name: "color",
        type: "string"
      },
      {
        name: "bounce",
        type: "string"
      },
      {
        name: "key",
        type: "string"
      }
    ],
    documented: true,
    category: "input"
  },
  {
    type: "wokwi-pushbutton",
    pins: [
      "1.l",
      "2.l",
      "1.r",
      "2.r"
    ],
    attrs: [
      {
        name: "color",
        type: "string"
      },
      {
        name: "bounce",
        type: "string"
      },
      {
        name: "key",
        type: "string"
      },
      {
        name: "xray",
        type: "string"
      },
      {
        name: "label",
        type: "string"
      }
    ],
    documented: true,
    category: "input"
  },
  {
    type: "wokwi-relay-module",
    pins: [
      "IN",
      "NO",
      "NC",
      "COM",
      "VCC",
      "GND"
    ],
    attrs: [
      {
        name: "transistor",
        type: "string",
        validValues: [
          "npn",
          "pnp"
        ]
      }
    ],
    documented: true,
    category: "motors"
  },
  {
    type: "wokwi-resistor",
    pins: [
      "1",
      "2"
    ],
    attrs: [
      {
        name: "value",
        type: "string"
      }
    ],
    documented: true,
    category: "passive"
  },
  {
    type: "wokwi-rgb-led",
    pins: [
      "COM",
      "R",
      "G",
      "B"
    ],
    attrs: [
      {
        name: "common",
        type: "string",
        validValues: [
          "anode",
          "cathode"
        ]
      },
      {
        name: "fps",
        type: "number"
      }
    ],
    documented: true,
    category: "leds"
  },
  {
    type: "wokwi-rotary-dialer",
    pins: [
      "GND",
      "DIAL",
      "PULSE"
    ],
    documented: false,
    category: "input"
  },
  {
    type: "wokwi-servo",
    pins: [
      "GND",
      "V+",
      "PWM"
    ],
    attrs: [
      {
        name: "horn",
        type: "string",
        validValues: [
          "single",
          "double",
          "cross"
        ]
      },
      {
        name: "hornColor",
        type: "string"
      }
    ],
    documented: true,
    category: "motors"
  },
  {
    type: "wokwi-slide-potentiometer",
    pins: [
      "GND",
      "SIG",
      "VCC"
    ],
    attrs: [
      {
        name: "value",
        type: "number"
      },
      {
        name: "travelLength",
        type: "number"
      }
    ],
    documented: true,
    category: "input"
  },
  {
    type: "wokwi-slide-switch",
    pins: [
      "1",
      "2",
      "3"
    ],
    attrs: [
      {
        name: "bounce",
        type: "string"
      }
    ],
    documented: true,
    category: "input"
  },
  {
    type: "wokwi-splendida",
    pins: [
      "DIN",
      "VDD",
      "VSS",
      "DOUT"
    ],
    documented: false,
    category: "leds"
  },
  {
    type: "wokwi-ssd1306",
    pins: [
      "DATA",
      "CLK",
      "DC",
      "RST",
      "CS",
      "3V3",
      "GND",
      "VIN"
    ],
    attrs: [
      {
        name: "i2cAddress",
        type: "string"
      },
      {
        name: "i2c-address",
        type: "string"
      }
    ],
    documented: true,
    category: "displays"
  },
  {
    type: "wokwi-stepper-motor",
    pins: [
      "A-",
      "A+",
      "B+",
      "B-"
    ],
    attrs: [
      {
        name: "arrow",
        type: "string"
      },
      {
        name: "display",
        type: "string",
        validValues: [
          "angle",
          "steps"
        ]
      },
      {
        name: "gearRatio",
        type: "number"
      },
      {
        name: "size",
        type: "string"
      }
    ],
    documented: true,
    category: "motors"
  },
  {
    type: "wokwi-text",
    pins: [],
    attrs: [
      {
        name: "text",
        type: "string"
      },
      {
        name: "fontSize",
        type: "number"
      },
      {
        name: "fontFamily",
        type: "string"
      },
      {
        name: "color",
        type: "string"
      }
    ],
    documented: true,
    category: "misc"
  },
  {
    type: "wokwi-tinypico",
    pins: [
      "$APA_PWR",
      "$APA_CLK",
      "$APA_DATA",
      "GND",
      "3V3",
      "4",
      "5",
      "14",
      "15",
      "18",
      "19",
      "21",
      "22",
      "23",
      "25",
      "26",
      "27",
      "32",
      "33"
    ],
    documented: false,
    isBoard: true,
    category: "boards"
  },
  {
    type: "wokwi-tm1637-7segment",
    pins: [
      "CLK",
      "DIO",
      "GND",
      "VCC"
    ],
    attrs: [
      {
        name: "color",
        type: "string"
      }
    ],
    documented: true,
    category: "displays"
  },
  {
    type: "wokwi-tv",
    pins: [
      "IN",
      "SYNC",
      "GND"
    ],
    documented: true,
    category: "displays"
  },
  {
    type: "wokwi-vcc",
    pins: [
      "VCC"
    ],
    attrs: [
      {
        name: "voltage",
        type: "number"
      }
    ],
    documented: false,
    category: "power"
  }
];

// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/registry/part-definitions.js
var partDefinitions = parts_default;

// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/registry/part-registry.js
class PartRegistry {
  constructor() {
    this.parts = new Map;
    for (const part of partDefinitions) {
      this.parts.set(part.type, part);
    }
  }
  loadBoardsBundle(bundle) {
    let count = 0;
    for (const [boardId, entry] of Object.entries(bundle)) {
      const partType = `board-${boardId}`;
      const pins = Object.keys(entry.def.pins || {}).sort((a, b) => {
        const aNum = parseFloat(a);
        const bNum = parseFloat(b);
        const aIsNum = !isNaN(aNum);
        const bIsNum = !isNaN(bNum);
        if (aIsNum && bIsNum)
          return aNum - bNum;
        if (aIsNum)
          return -1;
        if (bIsNum)
          return 1;
        return a.localeCompare(b);
      });
      const existing = this.parts.get(partType);
      this.parts.set(partType, {
        type: partType,
        pins,
        documented: existing?.documented ?? false,
        isBoard: true,
        category: "boards"
      });
      count++;
    }
    return count;
  }
  has(type) {
    return this.parts.has(type);
  }
  isBoard(type) {
    return this.parts.get(type)?.isBoard ?? false;
  }
  isDocumented(type) {
    return this.parts.get(type)?.documented ?? false;
  }
  isValidPin(type, pin) {
    const part = this.parts.get(type);
    return part ? part.pins.includes(pin) : false;
  }
  getPins(type) {
    return this.parts.get(type)?.pins ?? [];
  }
  getAttributes(type) {
    return this.parts.get(type)?.attrs ?? [];
  }
  isCustomChip(type) {
    return type.startsWith("chip-");
  }
  isCustomBoard(type) {
    return type.startsWith("board-") && !this.parts.has(type);
  }
}

// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/rules/rule.js
function createIssue(rule, message, options) {
  return {
    rule: rule.id,
    severity: options?.severity ?? rule.defaultSeverity,
    message,
    partId: options?.partId,
    connectionIndex: options?.connectionIndex,
    context: options?.context
  };
}
// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/rules/duplicate-id.js
var duplicateIdRule = {
  id: "duplicate-id",
  name: "Duplicate Part ID",
  description: "Checks for parts with duplicate IDs",
  defaultSeverity: "error",
  check(ctx) {
    const issues = [];
    const seenIds = new Map;
    for (let i = 0;i < ctx.diagram.parts.length; i++) {
      const part = ctx.diagram.parts[i];
      const existingIndex = seenIds.get(part.id);
      if (existingIndex !== undefined) {
        issues.push(createIssue(this, `Duplicate part ID "${part.id}" (first occurrence at index ${existingIndex})`, {
          partId: part.id,
          context: { firstIndex: existingIndex, secondIndex: i }
        }));
      } else {
        seenIds.set(part.id, i);
      }
    }
    return issues;
  }
};
// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/rules/invalid-attribute.js
var invalidAttributeRule = {
  id: "invalid-attribute",
  name: "Invalid Attribute",
  description: "Checks for unknown or invalid attribute names and values",
  defaultSeverity: "warning",
  check(ctx) {
    const issues = [];
    for (const part of ctx.diagram.parts) {
      if (!part.attrs)
        continue;
      if (!ctx.registry.has(part.type) || ctx.registry.isCustomChip(part.type)) {
        continue;
      }
      const knownAttrs = ctx.registry.getAttributes(part.type);
      if (knownAttrs.length === 0)
        continue;
      for (const [attrName, attrValue] of Object.entries(part.attrs)) {
        const attrDef = knownAttrs.find((a) => a.name === attrName);
        if (!attrDef) {
          issues.push(createIssue(this, `Unknown attribute "${attrName}" for part "${part.id}" (type: ${part.type})`, {
            partId: part.id,
            context: {
              attrName,
              attrValue,
              partType: part.type,
              knownAttrs: knownAttrs.map((a) => a.name)
            }
          }));
        } else if (attrDef.validValues && !attrDef.validValues.includes(attrValue)) {
          issues.push(createIssue(this, `Invalid value "${attrValue}" for attribute "${attrName}" on part "${part.id}". Valid values: ${attrDef.validValues.join(", ")}`, {
            partId: part.id,
            context: {
              attrName,
              attrValue,
              validValues: attrDef.validValues
            }
          }));
        }
      }
    }
    return issues;
  }
};
// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/utils/connection-parser.js
function parseEndpoint(endpoint) {
  const colonIndex = endpoint.indexOf(":");
  if (colonIndex === -1) {
    return { partId: endpoint, pin: "" };
  }
  return {
    partId: endpoint.substring(0, colonIndex),
    pin: endpoint.substring(colonIndex + 1)
  };
}

// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/rules/invalid-pin.js
function isBreadboard(type) {
  return type.startsWith("wokwi-breadboard");
}
function isValidBreadboardPin(pin) {
  const rowPinPattern = /^([1-9]|[1-5][0-9]|6[0-3])[tb]\.[a-j]$/;
  const powerRailPattern = /^[tb][pn]\.([1-9]|[1-4][0-9]|50)$/;
  return rowPinPattern.test(pin) || powerRailPattern.test(pin);
}
var invalidPinRule = {
  id: "invalid-pin",
  name: "Invalid Pin",
  description: "Checks for connections using non-existent pins",
  defaultSeverity: "error",
  check(ctx) {
    const issues = [];
    for (let i = 0;i < ctx.diagram.connections.length; i++) {
      const [source, target] = ctx.diagram.connections[i];
      const { partId: sourcePartId, pin: sourcePin } = parseEndpoint(source);
      const { partId: targetPartId, pin: targetPin } = parseEndpoint(target);
      const sourcePart = ctx.diagram.parts.find((p) => p.id === sourcePartId);
      const targetPart = ctx.diagram.parts.find((p) => p.id === targetPartId);
      if (sourcePart && sourcePin) {
        if (!ctx.registry.isCustomChip(sourcePart.type)) {
          if (isBreadboard(sourcePart.type)) {
            if (!isValidBreadboardPin(sourcePin)) {
              issues.push(createIssue(this, `Invalid breadboard pin "${sourcePin}" for part "${sourcePartId}". Expected format: row (e.g., "5t.a") or power rail (e.g., "tp.1")`, {
                connectionIndex: i,
                partId: sourcePartId,
                context: { pin: sourcePin, partType: sourcePart.type }
              }));
            }
          } else if (ctx.registry.has(sourcePart.type) && !ctx.registry.isValidPin(sourcePart.type, sourcePin)) {
            const validPins = ctx.registry.getPins(sourcePart.type);
            issues.push(createIssue(this, `Invalid pin "${sourcePin}" for part "${sourcePartId}" (type: ${sourcePart.type}). Valid pins: ${validPins.join(", ") || "none"}`, {
              connectionIndex: i,
              partId: sourcePartId,
              context: { pin: sourcePin, partType: sourcePart.type, validPins }
            }));
          }
        }
      }
      if (targetPart && targetPin) {
        if (!ctx.registry.isCustomChip(targetPart.type)) {
          if (isBreadboard(targetPart.type)) {
            if (!isValidBreadboardPin(targetPin)) {
              issues.push(createIssue(this, `Invalid breadboard pin "${targetPin}" for part "${targetPartId}". Expected format: row (e.g., "5t.a") or power rail (e.g., "tp.1")`, {
                connectionIndex: i,
                partId: targetPartId,
                context: { pin: targetPin, partType: targetPart.type }
              }));
            }
          } else if (ctx.registry.has(targetPart.type) && !ctx.registry.isValidPin(targetPart.type, targetPin)) {
            const validPins = ctx.registry.getPins(targetPart.type);
            issues.push(createIssue(this, `Invalid pin "${targetPin}" for part "${targetPartId}" (type: ${targetPart.type}). Valid pins: ${validPins.join(", ") || "none"}`, {
              connectionIndex: i,
              partId: targetPartId,
              context: { pin: targetPin, partType: targetPart.type, validPins }
            }));
          }
        }
      }
    }
    return issues;
  }
};
// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/rules/misplaced-coords.js
var COORD_ATTRS = ["top", "left", "rotate"];
var misplacedCoordsRule = {
  id: "misplaced-coords",
  name: "Misplaced Coordinates",
  description: 'Checks for "top", "left", or "rotate" in attrs instead of at the part level',
  defaultSeverity: "warning",
  check(ctx) {
    const issues = [];
    for (const part of ctx.diagram.parts) {
      if (!part.attrs)
        continue;
      for (const coordAttr of COORD_ATTRS) {
        if (coordAttr in part.attrs) {
          issues.push(createIssue(this, `"${coordAttr}" should be a property of the part, not in "attrs". Move it outside of attrs.`, {
            partId: part.id,
            context: { attr: coordAttr, value: part.attrs[coordAttr] }
          }));
        }
      }
    }
    return issues;
  }
};
// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/rules/missing-component.js
var missingComponentRule = {
  id: "missing-component",
  name: "Missing Component",
  description: "Checks for connections referencing parts that do not exist",
  defaultSeverity: "error",
  check(ctx) {
    const issues = [];
    const partIds = new Set(ctx.diagram.parts.map((p) => p.id));
    partIds.add("$serialMonitor");
    for (let i = 0;i < ctx.diagram.connections.length; i++) {
      const [source, target] = ctx.diagram.connections[i];
      const sourcePartId = parseEndpoint(source).partId;
      const targetPartId = parseEndpoint(target).partId;
      if (!partIds.has(sourcePartId)) {
        issues.push(createIssue(this, `Connection references non-existent part "${sourcePartId}"`, {
          connectionIndex: i,
          context: { missingPartId: sourcePartId, position: "source" }
        }));
      }
      if (!partIds.has(targetPartId)) {
        issues.push(createIssue(this, `Connection references non-existent part "${targetPartId}"`, {
          connectionIndex: i,
          context: { missingPartId: targetPartId, position: "target" }
        }));
      }
    }
    return issues;
  }
};
// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/rules/redundant-parts.js
var EXCLUDED_TYPES = [
  "wokwi-text",
  "wokwi-logo",
  "wokwi-ir-remote"
];
var redundantPartsRule = {
  id: "redundant-parts",
  name: "Redundant Parts",
  description: "Checks for parts that have no connections (excluding boards)",
  defaultSeverity: "warning",
  check(ctx) {
    const issues = [];
    const connectedPartIds = new Set;
    for (const [source, target] of ctx.diagram.connections) {
      connectedPartIds.add(parseEndpoint(source).partId);
      connectedPartIds.add(parseEndpoint(target).partId);
    }
    for (const part of ctx.diagram.parts) {
      if (ctx.registry.isBoard(part.type)) {
        continue;
      }
      if (EXCLUDED_TYPES.includes(part.type)) {
        continue;
      }
      if (ctx.registry.isCustomChip(part.type)) {
        continue;
      }
      if (!connectedPartIds.has(part.id)) {
        issues.push(createIssue(this, `Part "${part.id}" (type: ${part.type}) has no connections`, {
          partId: part.id,
          context: { partType: part.type }
        }));
      }
    }
    return issues;
  }
};
// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/rules/unknown-part-type.js
var unknownPartTypeRule = {
  id: "unknown-part-type",
  name: "Unknown Part Type",
  description: "Checks for parts with unrecognized types",
  defaultSeverity: "error",
  check(ctx) {
    const issues = [];
    for (const part of ctx.diagram.parts) {
      if (ctx.registry.isCustomChip(part.type) || ctx.registry.isCustomBoard(part.type)) {
        continue;
      }
      if (!ctx.registry.has(part.type)) {
        issues.push(createIssue(this, `Unknown part type "${part.type}" for part "${part.id}"`, {
          partId: part.id,
          context: { partType: part.type }
        }));
      }
    }
    return issues;
  }
};
// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/rules/unsupported-part.js
var unsupportedPartRule = {
  id: "unsupported-part",
  name: "Unsupported Part",
  description: "Warns about parts that are not in the official documentation",
  defaultSeverity: "info",
  check(ctx) {
    const issues = [];
    for (const part of ctx.diagram.parts) {
      if (!ctx.registry.has(part.type)) {
        continue;
      }
      if (ctx.registry.isCustomChip(part.type) || ctx.registry.isCustomBoard(part.type)) {
        continue;
      }
      if (!ctx.registry.isDocumented(part.type)) {
        issues.push(createIssue(this, `Part "${part.id}" uses undocumented type "${part.type}". This part may change or be removed in future versions.`, {
          partId: part.id,
          context: { partType: part.type }
        }));
      }
    }
    return issues;
  }
};
// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/rules/wrong-coord-names.js
var wrongCoordNamesRule = {
  id: "wrong-coord-names",
  name: "Wrong Coordinate Names",
  description: 'Checks for "x" or "y" instead of "left" or "top"',
  defaultSeverity: "error",
  check(ctx) {
    const issues = [];
    for (const part of ctx.diagram.parts) {
      const partAny = part;
      if ("x" in partAny) {
        issues.push(createIssue(this, `Part "${part.id}" uses "x" instead of "left" for horizontal position`, {
          partId: part.id,
          context: { wrongProp: "x", correctProp: "left", value: partAny.x }
        }));
      }
      if ("y" in partAny) {
        issues.push(createIssue(this, `Part "${part.id}" uses "y" instead of "top" for vertical position`, {
          partId: part.id,
          context: { wrongProp: "y", correctProp: "top", value: partAny.y }
        }));
      }
      if (part.attrs) {
        if ("x" in part.attrs) {
          issues.push(createIssue(this, `Part "${part.id}" has "x" in attrs instead of "left" at part level`, {
            partId: part.id,
            context: { wrongProp: "x", correctProp: "left", inAttrs: true }
          }));
        }
        if ("y" in part.attrs) {
          issues.push(createIssue(this, `Part "${part.id}" has "y" in attrs instead of "top" at part level`, {
            partId: part.id,
            context: { wrongProp: "y", correctProp: "top", inAttrs: true }
          }));
        }
      }
    }
    return issues;
  }
};
// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/rules/index.js
var allRules = [
  duplicateIdRule,
  invalidPinRule,
  missingComponentRule,
  unknownPartTypeRule,
  invalidAttributeRule,
  misplacedCoordsRule,
  redundantPartsRule,
  wrongCoordNamesRule,
  unsupportedPartRule
];

// ../../../../tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/linter.js
class DiagramLinter {
  constructor(options) {
    this.registry = new PartRegistry;
    this.rules = [...allRules];
    this.ruleConfigs = new Map;
    if (options?.rules) {
      for (const [ruleId, config] of Object.entries(options.rules)) {
        if (typeof config === "boolean") {
          this.ruleConfigs.set(ruleId, { enabled: config });
        } else {
          this.ruleConfigs.set(ruleId, config);
        }
      }
    }
  }
  lint(diagram) {
    const issues = [];
    const ctx = { diagram, registry: this.registry };
    for (const rule of this.rules) {
      const config = this.ruleConfigs.get(rule.id);
      if (config?.enabled === false) {
        continue;
      }
      const severityOverride = config?.severity;
      const ruleIssues = rule.check(ctx);
      for (const issue of ruleIssues) {
        if (severityOverride) {
          issue.severity = severityOverride;
        }
        issues.push(issue);
      }
    }
    const stats = {
      errors: issues.filter((i) => i.severity === "error").length,
      warnings: issues.filter((i) => i.severity === "warning").length,
      infos: issues.filter((i) => i.severity === "info").length,
      total: issues.length
    };
    return {
      valid: stats.errors === 0,
      issues,
      stats
    };
  }
  lintJSON(json) {
    try {
      const diagram = JSON.parse(json);
      return this.lint(diagram);
    } catch (error) {
      return {
        valid: false,
        issues: [
          {
            rule: "json-parse",
            severity: "error",
            message: `Failed to parse JSON: ${error instanceof Error ? error.message : String(error)}`
          }
        ],
        stats: {
          errors: 1,
          warnings: 0,
          infos: 0,
          total: 1
        }
      };
    }
  }
  getRegistry() {
    return this.registry;
  }
  setRuleEnabled(ruleId, enabled) {
    const existing = this.ruleConfigs.get(ruleId) ?? {};
    this.ruleConfigs.set(ruleId, { ...existing, enabled });
  }
  setRuleSeverity(ruleId, severity) {
    const existing = this.ruleConfigs.get(ruleId) ?? {};
    this.ruleConfigs.set(ruleId, { ...existing, severity });
  }
  getRuleIds() {
    return this.rules.map((r) => r.id);
  }
  getRule(ruleId) {
    return this.rules.find((r) => r.id === ruleId);
  }
}
// lib/board.ts
import { readFileSync } from "node:fs";
var BOARD_FROM_CALLER = process.env.SPARK_BOARD_JSON;
if (!BOARD_FROM_CALLER) {
  throw new Error("SPARK_BOARD_JSON is not set, so this does not know which board it is converting. " + "It names the DESIGN's resolved board file — spark's spine sets it; set it yourself when " + "running this by hand. There is deliberately no default: a converter that guesses the " + "board silently converts one design against another's pin map.");
}
var board = JSON.parse(readFileSync(BOARD_FROM_CALLER, "utf8"));

// lib/geometry.ts
var GRID_PX = 9.6;
var SIZES = {
  [board.wokwi_part_type]: board.physical.wokwi_size_px,
  "wokwi-pushbutton": { width: 70, height: 40 },
  "board-ssd1306": { width: 150, height: 120 },
  "wokwi-led": { width: 20, height: 40 },
  "wokwi-resistor": { width: 60, height: 20 },
  "chip-vl6180x": { width: 80, height: 60 },
  "chip-l9110s": { width: 80, height: 60 }
};
var DEFAULT_SIZE = { width: 80, height: 60 };
function sizeOf(wokwiType) {
  return SIZES[wokwiType] ?? DEFAULT_SIZE;
}
function snapToGrid(value) {
  return Math.round(value / GRID_PX) * GRID_PX;
}

class PinOracle {
  registry = new PartRegistry;
  chipPins = new Map;
  constructor(chipsDirectory) {
    if (chipsDirectory)
      this.loadChips(chipsDirectory);
  }
  loadChips(directory) {
    let entries;
    try {
      entries = readdirSync(directory);
    } catch {
      return;
    }
    for (const entry of entries) {
      if (!entry.endsWith(".chip.json"))
        continue;
      try {
        const definition = JSON.parse(readFileSync2(join(directory, entry), "utf8"));
        const chipName = entry.replace(/\.chip\.json$/, "");
        const pins = (definition.pins ?? []).filter((pin) => pin !== "");
        this.chipPins.set(`chip-${chipName}`, pins);
      } catch {}
    }
  }
  knowsPart(wokwiType) {
    return this.pinsOf(wokwiType).length > 0;
  }
  pinsOf(wokwiType) {
    const chip = this.chipPins.get(wokwiType);
    if (chip)
      return chip;
    try {
      return this.registry.getPins(wokwiType) ?? [];
    } catch {
      return [];
    }
  }
  isValidPin(wokwiType, pin) {
    if (!this.knowsPart(wokwiType))
      return true;
    return this.pinsOf(wokwiType).includes(pin);
  }
}

// lib/mapping.ts
import { readFileSync as readFileSync3 } from "node:fs";
var fromRecords = {};
function loadMappingFile(path) {
  useMappings(JSON.parse(readFileSync3(path, "utf8")));
  return Object.keys(fromRecords).length;
}
function useMappings(entries) {
  fromRecords = entries;
}
var WOKWI_NAMES_PINS_BY_GPIO = board.wokwi_pin_naming === "gpio";
var WOKWI_PINS = (() => {
  const byName = {};
  const aliases = board.physical?.pad_aliases ?? {};
  for (const [name, gpio] of Object.entries(board.pins)) {
    byName[name] = WOKWI_NAMES_PINS_BY_GPIO ? String(gpio) : name;
    const pad = aliases[name];
    if (pad !== undefined) {
      byName[pad] = WOKWI_NAMES_PINS_BY_GPIO ? String(gpio) : pad;
    }
  }
  return { ...byName, ...board.wokwi_power_pins ?? {} };
})();
var BOARD = {
  match: "Mcu",
  wokwiType: board.wokwi_part_type,
  pins: WOKWI_PINS
};
var PARTS = [
  BOARD,
  {
    match: /^Btn|Button/,
    wokwiType: "wokwi-pushbutton",
    pins: { A: "1.l", B: "2.l", pin1: "1.l", pin2: "2.l" },
    attrs: { color: "green" },
    side: "left"
  },
  {
    match: /Oled|SSD1306/,
    wokwiType: "board-ssd1306",
    pins: { VCC: "VCC", GND: "GND", SDA: "SDA", SCL: "SCL" },
    side: "right"
  },
  {
    match: /SensorHeader|Ir(Sensor)?|Tof|Rangefinder|Vl6180/i,
    wokwiType: "chip-vl6180x",
    pins: {
      VIN: "VIN",
      VCC: "VIN",
      GND: "GND",
      SDA: "SDA",
      SCL: "SCL",
      INT: "INT",
      OUT: "INT",
      GPIO1: "INT"
    },
    attrs: { distance: "200" },
    side: "right"
  },
  {
    match: /^MotorDriver$|L9110/i,
    wokwiType: "chip-l9110s",
    pins: {
      AIA: "IA",
      AIB: "IB",
      AIN1: "IA",
      AIN2: "IB",
      AO1: "OA",
      AO2: "OB",
      GND: "GND",
      BIA: null,
      BIB: null,
      PWMA: null,
      STBY: null,
      VM: null,
      VCC: null
    },
    side: "left"
  },
  {
    match: /StatusLed/,
    wokwiType: "wokwi-rgb-led",
    pins: { RED: "R", GREEN: "G", CATHODE: "COM", BLUE: "B" },
    side: "right"
  },
  {
    match: /^Led/,
    wokwiType: "wokwi-led",
    pins: { anode: "A", cathode: "C", pin1: "A", pin2: "C" },
    attrs: { color: "red" },
    side: "right"
  },
  {
    match: /^R\d|Resistor|^Pullup/,
    wokwiType: "wokwi-resistor",
    pins: { pin1: "1", pin2: "2", anode: "1", cathode: "2", left: "1", right: "2" },
    side: "right"
  }
];
var SKIP = [
  {
    match: /^(Decoup|Motor(Bulk|Brush))|Cap$/,
    reason: "decoupling and bulk capacitors do nothing in a digital simulation"
  },
  {
    match: /^BinConnector$|PowerInlet|^Jst/i,
    reason: "a connector is wiring, not a part to simulate. Matched by KIND rather than by one " + "board's name for it, so a generated design naming its inlet after the part is covered " + "too"
  },
  { match: /^Speaker$/, reason: "no Wokwi part; the firmware's log says which cue it played" },
  {
    match: /^(CurrentShunt|PulldownIa|PulldownIb)$/,
    reason: "hardware with no behaviour to simulate: a sense shunt, and the pulldowns that hold " + "the motor still while the board boots"
  },
  { match: /^AudioAmp$/, reason: "no Wokwi part for the I2S amplifier; cues are visible in the serial log" },
  {
    match: /^(TofInt|BtnOpen)Pull(up|down)$/,
    reason: "these hold a deep-sleep wake input at a defined level while the chip is off. Wokwi " + "does not wake this chip from a GPIO at all and has no floating-input model, so every " + "part it drives is driven — the exact condition these resistors exist for cannot be " + "simulated here, and must be checked on the bench. Matched in BOTH directions because " + "which one they are is the board's decision, not this file's: they became pull-DOWNS " + "when the wake sources moved to 3V3, and a rule naming only one spelling silently " + "stopped covering them"
  },
  {
    match: /^(Sda|Scl)Pullup$/,
    reason: "Wokwi's I2C is idealised — its bus reads back correctly with no pull-ups at all, " + "so simulating them proves nothing. Which is exactly why their absence on the real " + "board went unnoticed: no simulation could ever have caught it"
  }
];
function findMapping(componentName) {
  const entry = fromRecords[componentName];
  if (entry?.wokwiType) {
    return { match: componentName, wokwiType: entry.wokwiType, pins: entry.pins, attrs: entry.attrs, side: entry.side };
  }
  return PARTS.find((part) => matches(part.match, componentName));
}
function findSkipRule(componentName) {
  const entry = fromRecords[componentName];
  if (entry?.skip)
    return { match: componentName, reason: entry.skip };
  return SKIP.find((rule) => matches(rule.match, componentName));
}
function matches(pattern, name) {
  return typeof pattern === "string" ? pattern === name : pattern.test(name);
}
function wokwiPinName(mapping, designPin) {
  if (mapping.pins && designPin in mapping.pins)
    return mapping.pins[designPin] ?? null;
  return designPin;
}

// lib/placement.ts
var PART_GAP_PX = GRID_PX * 4;
var COLUMN_GAP_PX = GRID_PX * 12;

class ColumnPlacer {
  boardType;
  constructor(boardType = board.wokwi_part_type) {
    this.boardType = boardType;
  }
  place(parts) {
    const placements = new Map;
    const board2 = parts.find((part) => part.wokwiType === this.boardType);
    const boardSize = sizeOf(this.boardType);
    if (board2)
      placements.set(board2.id, { top: 0, left: 0 });
    const columns = {
      left: { x: -(COLUMN_GAP_PX + sizeOf("board-ssd1306").width), y: 0 },
      right: { x: boardSize.width + COLUMN_GAP_PX, y: 0 }
    };
    for (const part of parts) {
      if (part === board2)
        continue;
      const column = columns[part.side];
      placements.set(part.id, {
        left: snapToGrid(column.x),
        top: snapToGrid(column.y)
      });
      column.y += sizeOf(part.wokwiType).height + PART_GAP_PX;
    }
    return placements;
  }
}

// lib/emitters/wokwi.ts
var GROUND_WIRE = "black";
var POWER_WIRE = "red";
var SIGNAL_WIRE = "green";
function emitWokwiDiagram(netlist, options = {}) {
  const problems = [];
  const skipped = [];
  const oracle = new PinOracle(options.chipsDirectory);
  const mapped = mapComponents(netlist, problems, skipped);
  const placer = options.placer ?? new ColumnPlacer;
  const placements = placer.place(mapped.parts);
  const diagram = {
    version: 1,
    author: options.author ?? "generated from board.tsx",
    editor: "wokwi",
    parts: mapped.parts.map((part) => ({
      type: part.wokwiType,
      id: part.id,
      top: placements.get(part.id)?.top ?? 0,
      left: placements.get(part.id)?.left ?? 0,
      attrs: mapped.mappingByPartId.get(part.id)?.attrs ?? {}
    })),
    connections: []
  };
  const netOutcomes = [];
  diagram.connections = wireNets(netlist, mapped, oracle, problems, netOutcomes);
  return { diagram, problems, skipped, netOutcomes };
}
function mapComponents(netlist, problems, skipped) {
  const parts = [];
  const partIdByComponent = new Map;
  const mappingByComponent = new Map;
  const mappingByPartId = new Map;
  for (const component of netlist.components) {
    const skipRule = findSkipRule(component.name);
    if (skipRule) {
      skipped.push({ component: component.name, reason: skipRule.reason });
      continue;
    }
    const mapping = findMapping(component.name);
    if (!mapping) {
      problems.push({
        message: "no Wokwi part is mapped to this component. Say in its part record how it is " + "simulated (`simulation`: a stand-in part, a chip, or a skip with its reason), or " + "add it to lib/mapping.ts for a hand-written board",
        context: { component: component.name }
      });
      continue;
    }
    const partId = component.name.toLowerCase();
    parts.push({ id: partId, wokwiType: mapping.wokwiType, side: mapping.side ?? "right" });
    partIdByComponent.set(component.id, partId);
    mappingByComponent.set(component.id, mapping);
    mappingByPartId.set(partId, mapping);
  }
  return { parts, partIdByComponent, mappingByComponent, mappingByPartId };
}
function wireNets(netlist, mapped, oracle, problems, netOutcomes) {
  const connections = [];
  for (const net of netlist.nets) {
    const endpoints = [];
    let skippedEndpoints = 0;
    for (const member of net.members) {
      const partId = mapped.partIdByComponent.get(member.componentId);
      const mapping = mapped.mappingByComponent.get(member.componentId);
      if (!partId || !mapping) {
        skippedEndpoints += 1;
        continue;
      }
      const pin = wokwiPinName(mapping, member.pinName);
      if (pin === null) {
        skippedEndpoints += 1;
        continue;
      }
      if (!oracle.isValidPin(mapping.wokwiType, pin)) {
        problems.push({
          message: `"${pin}" is not a pin of ${mapping.wokwiType}. Valid pins: ` + oracle.pinsOf(mapping.wokwiType).join(", "),
          context: { component: partId, pin: member.pinName, net: net.name ?? net.id }
        });
        continue;
      }
      endpoints.push({ partId, pin, isBoard: mapping.wokwiType === BOARD.wokwiType });
    }
    const outcome = {
      netId: net.id,
      name: net.name,
      simulatedEndpoints: endpoints.length,
      skippedEndpoints,
      wires: 0
    };
    netOutcomes.push(outcome);
    if (endpoints.length < 2)
      continue;
    const colour = wireColour(net.name);
    const hub = endpoints.find((endpoint) => endpoint.isBoard) ?? endpoints[0];
    for (const endpoint of endpoints) {
      if (endpoint === hub)
        continue;
      connections.push([
        `${hub.partId}:${hub.pin}`,
        `${endpoint.partId}:${endpoint.pin}`,
        colour,
        []
      ]);
      outcome.wires += 1;
    }
  }
  return connections;
}
function wireColour(netName) {
  if (!netName)
    return SIGNAL_WIRE;
  if (/gnd|ground/i.test(netName))
    return GROUND_WIRE;
  if (/^v|power|vcc|vbat|3v3|5v/i.test(netName))
    return POWER_WIRE;
  return SIGNAL_WIRE;
}

// lib/merge.ts
var HAND_ADDED_ATTR = "handAdded";
function mergeWithExisting(generated, existing) {
  const summary = { keptPositions: 0, keptHandAddedParts: [], keptRoutes: 0 };
  if (!existing)
    return { diagram: generated, summary };
  const existingParts = new Map(existing.parts.map((part) => [part.id, part]));
  const parts = generated.parts.map((part) => {
    const previous = existingParts.get(part.id);
    if (!previous)
      return part;
    summary.keptPositions += 1;
    return {
      ...part,
      top: previous.top ?? part.top,
      left: previous.left ?? part.left,
      ...previous.rotate !== undefined ? { rotate: previous.rotate } : {},
      attrs: { ...previous.attrs, ...part.attrs }
    };
  });
  for (const part of existing.parts) {
    const isHandAdded = part.attrs?.[HAND_ADDED_ATTR] === "true";
    if (isHandAdded && !parts.some((candidate) => candidate.id === part.id)) {
      parts.push(part);
      summary.keptHandAddedParts.push(part.id);
    }
  }
  const connections = generated.connections.map((connection) => {
    const previous = findMatchingConnection(existing.connections, connection);
    if (previous && previous[3]?.length) {
      summary.keptRoutes += 1;
      return [connection[0], connection[1], connection[2], previous[3]];
    }
    return connection;
  });
  for (const connection of existing.connections) {
    const involvesHandAdded = summary.keptHandAddedParts.some((partId) => connection.some((end) => typeof end === "string" && end.startsWith(`${partId}:`)));
    if (involvesHandAdded)
      connections.push(connection);
  }
  return {
    diagram: { ...generated, parts, connections },
    summary
  };
}
function findMatchingConnection(connections, wanted) {
  return connections.find((candidate) => candidate[0] === wanted[0] && candidate[1] === wanted[1] || candidate[0] === wanted[1] && candidate[1] === wanted[0]);
}

// ../../../../tools/circuit-to-wokwi/node_modules/circuit-json/dist/index.mjs
var exports_dist = {};
__export(exports_dist, {
  all_layers: () => all_layers,
  any_circuit_element: () => any_circuit_element,
  any_soup_element: () => any_soup_element,
  any_source_component: () => any_source_component,
  asset: () => asset,
  base_circuit_json_error: () => base_circuit_json_error,
  battery_capacity: () => battery_capacity,
  brep_shape: () => brep_shape,
  cadModelDefaultDirectionMap: () => cadModelDefaultDirectionMap,
  cad_component: () => cad_component,
  cad_model_axis_directions: () => cad_model_axis_directions,
  cad_model_formats: () => cad_model_formats,
  capacitance: () => capacitance,
  circuit_json_footprint_load_error: () => circuit_json_footprint_load_error,
  current: () => current,
  distance: () => distance,
  duration_ms: () => duration_ms,
  experiment_type: () => experiment_type,
  external_footprint_load_error: () => external_footprint_load_error,
  frequency: () => frequency,
  getRotationBetweenPcbPin1Locations: () => getRotationBetweenPcbPin1Locations,
  getZodPrefixedIdWithDefault: () => getZodPrefixedIdWithDefault,
  inductance: () => inductance,
  insertionDirectionToCanonical: () => insertionDirectionToCanonical,
  insertionDirectionToVector: () => insertionDirectionToVector,
  insertion_direction: () => insertion_direction,
  kicadAt: () => kicadAt,
  kicadEffects: () => kicadEffects,
  kicadFont: () => kicadFont,
  kicadFootprintAttributes: () => kicadFootprintAttributes,
  kicadFootprintMetadata: () => kicadFootprintMetadata,
  kicadFootprintModel: () => kicadFootprintModel,
  kicadFootprintPad: () => kicadFootprintPad,
  kicadFootprintProperties: () => kicadFootprintProperties,
  kicadProperty: () => kicadProperty,
  kicadSymbolEffects: () => kicadSymbolEffects,
  kicadSymbolMetadata: () => kicadSymbolMetadata,
  kicadSymbolPinNames: () => kicadSymbolPinNames,
  kicadSymbolPinNumbers: () => kicadSymbolPinNumbers,
  kicadSymbolProperties: () => kicadSymbolProperties,
  kicadSymbolProperty: () => kicadSymbolProperty,
  layer_ref: () => layer_ref,
  layer_string: () => layer_string,
  length: () => length,
  manufacturing_drc_properties: () => manufacturing_drc_properties,
  ms: () => ms,
  ninePointAnchor: () => ninePointAnchor,
  parseAndConvertSiUnit: () => parseAndConvertSiUnit,
  pcbRenderLayer: () => pcbRenderLayer,
  pcb_autorouting_error: () => pcb_autorouting_error,
  pcb_bend: () => pcb_bend,
  pcb_board: () => pcb_board,
  pcb_breakout_point: () => pcb_breakout_point,
  pcb_bus_length_skew_error: () => pcb_bus_length_skew_error,
  pcb_component: () => pcb_component,
  pcb_component_invalid_layer_error: () => pcb_component_invalid_layer_error,
  pcb_component_missing_courtyard_warning: () => pcb_component_missing_courtyard_warning,
  pcb_component_not_on_board_edge_error: () => pcb_component_not_on_board_edge_error,
  pcb_component_outside_board_error: () => pcb_component_outside_board_error,
  pcb_connector_not_in_accessible_orientation_warning: () => pcb_connector_not_in_accessible_orientation_warning,
  pcb_copper_pour: () => pcb_copper_pour,
  pcb_copper_pour_brep: () => pcb_copper_pour_brep,
  pcb_copper_pour_polygon: () => pcb_copper_pour_polygon,
  pcb_copper_pour_rect: () => pcb_copper_pour_rect,
  pcb_copper_text: () => pcb_copper_text,
  pcb_courtyard_circle: () => pcb_courtyard_circle,
  pcb_courtyard_outline: () => pcb_courtyard_outline,
  pcb_courtyard_overlap_error: () => pcb_courtyard_overlap_error,
  pcb_courtyard_pill: () => pcb_courtyard_pill,
  pcb_courtyard_polygon: () => pcb_courtyard_polygon,
  pcb_courtyard_rect: () => pcb_courtyard_rect,
  pcb_cutout: () => pcb_cutout,
  pcb_cutout_circle: () => pcb_cutout_circle,
  pcb_cutout_path: () => pcb_cutout_path,
  pcb_cutout_polygon: () => pcb_cutout_polygon,
  pcb_cutout_rect: () => pcb_cutout_rect,
  pcb_debug_line: () => pcb_debug_line,
  pcb_debug_object: () => pcb_debug_object,
  pcb_debug_object_base: () => pcb_debug_object_base,
  pcb_debug_point: () => pcb_debug_point,
  pcb_debug_rect: () => pcb_debug_rect,
  pcb_fabrication_note_dimension: () => pcb_fabrication_note_dimension,
  pcb_fabrication_note_path: () => pcb_fabrication_note_path,
  pcb_fabrication_note_rect: () => pcb_fabrication_note_rect,
  pcb_fabrication_note_text: () => pcb_fabrication_note_text,
  pcb_fabricator_extra_charge_warning: () => pcb_fabricator_extra_charge_warning,
  pcb_footprint_overlap_error: () => pcb_footprint_overlap_error,
  pcb_ground_plane: () => pcb_ground_plane,
  pcb_ground_plane_region: () => pcb_ground_plane_region,
  pcb_group: () => pcb_group,
  pcb_hole: () => pcb_hole,
  pcb_hole_circle_or_square_shape: () => pcb_hole_circle_or_square_shape,
  pcb_hole_circle_shape: () => pcb_hole_circle_shape,
  pcb_hole_oval_shape: () => pcb_hole_oval_shape,
  pcb_hole_pill_shape: () => pcb_hole_pill_shape,
  pcb_hole_rect_shape: () => pcb_hole_rect_shape,
  pcb_hole_rotated_pill_shape: () => pcb_hole_rotated_pill_shape,
  pcb_keepout: () => pcb_keepout,
  pcb_keepout_outline: () => pcb_keepout_outline,
  pcb_keepout_overlap_warning: () => pcb_keepout_overlap_warning,
  pcb_manual_edit_conflict_warning: () => pcb_manual_edit_conflict_warning,
  pcb_missing_footprint_error: () => pcb_missing_footprint_error,
  pcb_net: () => pcb_net,
  pcb_note_dimension: () => pcb_note_dimension,
  pcb_note_line: () => pcb_note_line,
  pcb_note_path: () => pcb_note_path,
  pcb_note_rect: () => pcb_note_rect,
  pcb_note_text: () => pcb_note_text,
  pcb_packing_error: () => pcb_packing_error,
  pcb_pad_pad_clearance_error: () => pcb_pad_pad_clearance_error,
  pcb_pad_trace_clearance_error: () => pcb_pad_trace_clearance_error,
  pcb_panel: () => pcb_panel,
  pcb_panelization_placement_error: () => pcb_panelization_placement_error,
  pcb_pin1_location: () => pcb_pin1_location,
  pcb_placement_error: () => pcb_placement_error,
  pcb_plated_hole: () => pcb_plated_hole,
  pcb_port: () => pcb_port,
  pcb_port_not_connected_error: () => pcb_port_not_connected_error,
  pcb_port_not_matched_error: () => pcb_port_not_matched_error,
  pcb_preflight_routing_error: () => pcb_preflight_routing_error,
  pcb_route_hint: () => pcb_route_hint,
  pcb_route_hints: () => pcb_route_hints,
  pcb_silkscreen_circle: () => pcb_silkscreen_circle,
  pcb_silkscreen_graphic: () => pcb_silkscreen_graphic,
  pcb_silkscreen_graphic_brep: () => pcb_silkscreen_graphic_brep,
  pcb_silkscreen_line: () => pcb_silkscreen_line,
  pcb_silkscreen_oval: () => pcb_silkscreen_oval,
  pcb_silkscreen_path: () => pcb_silkscreen_path,
  pcb_silkscreen_pill: () => pcb_silkscreen_pill,
  pcb_silkscreen_rect: () => pcb_silkscreen_rect,
  pcb_silkscreen_text: () => pcb_silkscreen_text,
  pcb_smtpad: () => pcb_smtpad,
  pcb_smtpad_pill: () => pcb_smtpad_pill,
  pcb_solder_paste: () => pcb_solder_paste,
  pcb_stiffener: () => pcb_stiffener,
  pcb_stiffener_polygon: () => pcb_stiffener_polygon,
  pcb_stiffener_rect: () => pcb_stiffener_rect,
  pcb_text: () => pcb_text,
  pcb_thermal_spoke: () => pcb_thermal_spoke,
  pcb_trace: () => pcb_trace,
  pcb_trace_error: () => pcb_trace_error,
  pcb_trace_hint: () => pcb_trace_hint,
  pcb_trace_missing_error: () => pcb_trace_missing_error,
  pcb_trace_route_point: () => pcb_trace_route_point,
  pcb_trace_route_point_through_pad: () => pcb_trace_route_point_through_pad,
  pcb_trace_route_point_via: () => pcb_trace_route_point_via,
  pcb_trace_route_point_wire: () => pcb_trace_route_point_wire,
  pcb_trace_too_long_error: () => pcb_trace_too_long_error,
  pcb_trace_too_long_warning: () => pcb_trace_too_long_warning,
  pcb_trace_too_many_vias_warning: () => pcb_trace_too_many_vias_warning,
  pcb_trace_warning: () => pcb_trace_warning,
  pcb_via: () => pcb_via,
  pcb_via_clearance_error: () => pcb_via_clearance_error,
  pcb_via_trace_clearance_error: () => pcb_via_trace_clearance_error,
  point: () => point,
  point3: () => point3,
  point_with_bulge: () => point_with_bulge,
  port_arrangement: () => port_arrangement,
  position: () => position,
  position3: () => position3,
  resistance: () => resistance,
  ring: () => ring,
  rotation: () => rotation,
  route_hint_point: () => route_hint_point,
  schematic_arc: () => schematic_arc,
  schematic_box: () => schematic_box,
  schematic_circle: () => schematic_circle,
  schematic_component: () => schematic_component,
  schematic_component_overlap_warning: () => schematic_component_overlap_warning,
  schematic_component_port_arrangement_by_sides: () => schematic_component_port_arrangement_by_sides,
  schematic_component_port_arrangement_by_size: () => schematic_component_port_arrangement_by_size,
  schematic_component_styling_warning: () => schematic_component_styling_warning,
  schematic_debug_line: () => schematic_debug_line,
  schematic_debug_object: () => schematic_debug_object,
  schematic_debug_object_base: () => schematic_debug_object_base,
  schematic_debug_point: () => schematic_debug_point,
  schematic_debug_rect: () => schematic_debug_rect,
  schematic_element_outside_sheet_warning: () => schematic_element_outside_sheet_warning,
  schematic_error: () => schematic_error,
  schematic_graphic: () => schematic_graphic,
  schematic_group: () => schematic_group,
  schematic_layout_error: () => schematic_layout_error,
  schematic_line: () => schematic_line,
  schematic_manual_edit_conflict_warning: () => schematic_manual_edit_conflict_warning,
  schematic_missing_sheet_warning: () => schematic_missing_sheet_warning,
  schematic_net_label: () => schematic_net_label,
  schematic_path: () => schematic_path,
  schematic_pin_styles: () => schematic_pin_styles,
  schematic_port: () => schematic_port,
  schematic_rect: () => schematic_rect,
  schematic_sheet: () => schematic_sheet,
  schematic_sheet_size: () => schematic_sheet_size,
  schematic_symbol: () => schematic_symbol,
  schematic_table: () => schematic_table,
  schematic_table_cell: () => schematic_table_cell,
  schematic_text: () => schematic_text,
  schematic_text_part: () => schematic_text_part,
  schematic_trace: () => schematic_trace,
  schematic_voltage_probe: () => schematic_voltage_probe,
  simulation_ac_current_source: () => simulation_ac_current_source,
  simulation_ac_sweep_current_graph: () => simulation_ac_sweep_current_graph,
  simulation_ac_sweep_voltage_graph: () => simulation_ac_sweep_voltage_graph,
  simulation_ac_voltage_source: () => simulation_ac_voltage_source,
  simulation_complex_sample: () => simulation_complex_sample,
  simulation_current_probe: () => simulation_current_probe,
  simulation_current_source: () => simulation_current_source,
  simulation_dc_current_source: () => simulation_dc_current_source,
  simulation_dc_operating_point_current: () => simulation_dc_operating_point_current,
  simulation_dc_operating_point_voltage: () => simulation_dc_operating_point_voltage,
  simulation_dc_sweep_current_graph: () => simulation_dc_sweep_current_graph,
  simulation_dc_sweep_unit: () => simulation_dc_sweep_unit,
  simulation_dc_sweep_voltage_graph: () => simulation_dc_sweep_voltage_graph,
  simulation_dc_voltage_source: () => simulation_dc_voltage_source,
  simulation_experiment: () => simulation_experiment,
  simulation_op_amp: () => simulation_op_amp,
  simulation_oscilloscope_trace: () => simulation_oscilloscope_trace,
  simulation_parameter_sweep: () => simulation_parameter_sweep,
  simulation_parameter_sweep_coordinate: () => simulation_parameter_sweep_coordinate,
  simulation_parameter_type: () => simulation_parameter_type,
  simulation_parameter_unit: () => simulation_parameter_unit,
  simulation_spice_subcircuit: () => simulation_spice_subcircuit,
  simulation_switch: () => simulation_switch,
  simulation_transient_current_graph: () => simulation_transient_current_graph,
  simulation_transient_voltage_graph: () => simulation_transient_voltage_graph,
  simulation_unknown_experiment_error: () => simulation_unknown_experiment_error,
  simulation_voltage_probe: () => simulation_voltage_probe,
  simulation_voltage_source: () => simulation_voltage_source,
  size: () => size,
  source_ambiguous_port_reference: () => source_ambiguous_port_reference,
  source_board: () => source_board,
  source_bus: () => source_bus,
  source_component_base: () => source_component_base,
  source_component_internal_connection: () => source_component_internal_connection,
  source_component_misconfigured_error: () => source_component_misconfigured_error,
  source_component_pins_underspecified_warning: () => source_component_pins_underspecified_warning,
  source_confusing_net_name_warning: () => source_confusing_net_name_warning,
  source_failed_to_create_component_error: () => source_failed_to_create_component_error,
  source_group: () => source_group,
  source_i2c_misconfigured_error: () => source_i2c_misconfigured_error,
  source_interconnect: () => source_interconnect,
  source_invalid_component_property_error: () => source_invalid_component_property_error,
  source_manually_placed_via: () => source_manually_placed_via,
  source_missing_manufacturer_part_number_warning: () => source_missing_manufacturer_part_number_warning,
  source_missing_property_error: () => source_missing_property_error,
  source_net: () => source_net,
  source_no_ground_pin_defined_warning: () => source_no_ground_pin_defined_warning,
  source_no_power_pin_defined_warning: () => source_no_power_pin_defined_warning,
  source_part_not_found_warning: () => source_part_not_found_warning,
  source_pcb_ground_plane: () => source_pcb_ground_plane,
  source_pin_attributes: () => source_pin_attributes,
  source_pin_missing_trace_warning: () => source_pin_missing_trace_warning,
  source_pin_must_be_connected_error: () => source_pin_must_be_connected_error,
  source_port: () => source_port,
  source_project_metadata: () => source_project_metadata,
  source_property_ignored_warning: () => source_property_ignored_warning,
  source_refdes_convention_warning: () => source_refdes_convention_warning,
  source_simple_ammeter: () => source_simple_ammeter,
  source_simple_battery: () => source_simple_battery,
  source_simple_capacitor: () => source_simple_capacitor,
  source_simple_chip: () => source_simple_chip,
  source_simple_connector: () => source_simple_connector,
  source_simple_connector_standards: () => source_simple_connector_standards,
  source_simple_crystal: () => source_simple_crystal,
  source_simple_current_source: () => source_simple_current_source,
  source_simple_diode: () => source_simple_diode,
  source_simple_fiducial: () => source_simple_fiducial,
  source_simple_fuse: () => source_simple_fuse,
  source_simple_ground: () => source_simple_ground,
  source_simple_inductor: () => source_simple_inductor,
  source_simple_led: () => source_simple_led,
  source_simple_mosfet: () => source_simple_mosfet,
  source_simple_op_amp: () => source_simple_op_amp,
  source_simple_pin_header: () => source_simple_pin_header,
  source_simple_pinout: () => source_simple_pinout,
  source_simple_potentiometer: () => source_simple_potentiometer,
  source_simple_power_source: () => source_simple_power_source,
  source_simple_push_button: () => source_simple_push_button,
  source_simple_resistor: () => source_simple_resistor,
  source_simple_resonator: () => source_simple_resonator,
  source_simple_switch: () => source_simple_switch,
  source_simple_test_point: () => source_simple_test_point,
  source_simple_transistor: () => source_simple_transistor,
  source_simple_voltage_probe: () => source_simple_voltage_probe,
  source_simple_voltage_source: () => source_simple_voltage_source,
  source_trace: () => source_trace,
  source_trace_not_connected_error: () => source_trace_not_connected_error,
  source_unnamed_trace_warning: () => source_unnamed_trace_warning,
  spice_simulation_options: () => spice_simulation_options,
  supplier_footprint_mismatch_warning: () => supplier_footprint_mismatch_warning,
  supplier_name: () => supplier_name,
  time: () => time,
  timestamp: () => timestamp,
  unknown_error_finding_part: () => unknown_error_finding_part,
  visible_layer: () => visible_layer,
  voltage: () => voltage,
  wave_shape: () => wave_shape
});

// ../../../../tools/circuit-to-wokwi/node_modules/format-si-unit/dist/index.js
var SI_PREFIX_VALUES = /* @__PURE__ */ new Map([
  ["T", 1000000000000],
  ["G", 1e9],
  ["M", 1e6],
  ["K", 1000],
  ["k", 1000],
  ["", 1],
  ["m", 0.001],
  ["µ", 0.000001],
  ["μ", 0.000001],
  ["u", 0.000001],
  ["n", 0.000000001],
  ["p", 0.000000000001],
  ["f", 0.000000000000001]
]);
var SI_PREFIXES = [...SI_PREFIX_VALUES.keys()];
function getSiPrefixMultiplier(prefix) {
  return SI_PREFIX_VALUES.get(prefix);
}
var unitMappings = {
  Hz: {
    baseUnit: "Hz",
    variants: {
      MHz: 1e6,
      kHz: 1000,
      Hz: 1
    }
  },
  g: {
    baseUnit: "g",
    variants: {
      kg: 1000,
      g: 1
    }
  },
  Ω: {
    baseUnit: "Ω",
    variants: {
      mΩ: 0.001,
      mohm: 0.001,
      mOhm: 0.001,
      milliohm: 0.001,
      Ω: 1,
      ohm: 1,
      Ohm: 1,
      kΩ: 1000,
      KΩ: 1000,
      kohm: 1000,
      kOhm: 1000,
      KOhm: 1000,
      Kohm: 1000,
      MΩ: 1e6,
      Mohm: 1e6,
      MOhm: 1e6,
      megohm: 1e6,
      Megohm: 1e6,
      GΩ: 1e9,
      Gohm: 1e9,
      GOhm: 1e9,
      TΩ: 1000000000000,
      Tohm: 1000000000000,
      TOhm: 1000000000000
    }
  },
  V: {
    baseUnit: "V",
    variants: {
      mV: 0.001,
      V: 1,
      kV: 1000,
      KV: 1000,
      MV: 1e6,
      GV: 1e9,
      TV: 1000000000000
    }
  },
  A: {
    baseUnit: "A",
    variants: {
      µA: 0.000001,
      μA: 0.000001,
      mA: 0.001,
      ma: 0.001,
      A: 1,
      kA: 1000,
      MA: 1e6
    }
  },
  F: {
    baseUnit: "F",
    variants: {
      pF: 0.000000000001,
      nF: 0.000000001,
      µF: 0.000001,
      μF: 0.000001,
      uF: 0.000001,
      mF: 0.001,
      F: 1,
      kF: 1000,
      KF: 1000,
      MF: 1e6
    }
  },
  H: {
    baseUnit: "H",
    variants: {
      pH: 0.000000000001,
      nH: 0.000000001,
      µH: 0.000001,
      μH: 0.000001,
      uH: 0.000001,
      mH: 0.001,
      H: 1,
      kH: 1000,
      KH: 1000,
      MH: 1e6
    }
  },
  ml: {
    baseUnit: "ml",
    variants: {
      ml: 1,
      mL: 1,
      l: 1000,
      L: 1000
    }
  },
  deg: {
    baseUnit: "deg",
    variants: {
      rad: 180 / Math.PI
    }
  },
  ms: {
    baseUnit: "ms",
    variants: {
      fs: 0.000000000001,
      ps: 0.000000001,
      ns: 0.000001,
      us: 0.001,
      µs: 0.001,
      μs: 0.001,
      ms: 1,
      s: 1000
    }
  },
  mm: {
    baseUnit: "mm",
    variants: {
      nm: 0.000001,
      µm: 0.001,
      μm: 0.001,
      um: 0.001,
      mm: 1,
      cm: 10,
      dm: 100,
      m: 1000,
      km: 1e6,
      in: 25.4,
      ft: 304.8,
      IN: 25.4,
      FT: 304.8,
      yd: 914.4,
      mi: 1609344,
      mil: 0.0254
    }
  }
};
var unitMappingAndVariantSuffixes = /* @__PURE__ */ new Set;
for (const [baseUnit, info] of Object.entries(unitMappings)) {
  unitMappingAndVariantSuffixes.add(baseUnit);
  for (const variant of Object.keys(info.variants)) {
    unitMappingAndVariantSuffixes.add(variant);
  }
}
function getBaseTscircuitUnit(unit) {
  for (const info of Object.values(unitMappings)) {
    if (unit in info.variants) {
      return {
        baseUnit: info.baseUnit,
        conversionFactor: info.variants[unit]
      };
    }
    for (const [variant, conversionFactor] of Object.entries(info.variants)) {
      if (!unit.endsWith(variant))
        continue;
      const prefix = unit.slice(0, -variant.length);
      const prefixMultiplier = getSiPrefixMultiplier(prefix);
      if (prefixMultiplier == null)
        continue;
      return {
        baseUnit: info.baseUnit,
        conversionFactor: prefixMultiplier * conversionFactor
      };
    }
  }
  return {
    baseUnit: unit,
    conversionFactor: 1
  };
}
function parseAndConvertSiUnit(v, unitOfValue) {
  if (v === undefined || v === null)
    return { parsedUnit: null, unitOfValue: null, value: null };
  if (typeof v === "string" && v.match(/^-?[\d.]+$/))
    return {
      value: Number.parseFloat(v),
      parsedUnit: null,
      unitOfValue: null
    };
  if (typeof v === "number")
    return { value: v, parsedUnit: null, unitOfValue: null };
  if (typeof v === "object" && "x" in v && "y" in v) {
    const firstResult = parseAndConvertSiUnit(v.x, unitOfValue);
    const xResult = parseAndConvertSiUnit(v.x, unitOfValue);
    const yResult = parseAndConvertSiUnit(v.y, unitOfValue);
    if (xResult.value === null || yResult.value === null) {
      return { parsedUnit: null, unitOfValue: null, value: null };
    }
    return {
      parsedUnit: firstResult.parsedUnit,
      unitOfValue: firstResult.unitOfValue,
      value: {
        x: xResult.value,
        y: yResult.value
      }
    };
  }
  const reversedInputString = v.toString().split("").reverse().join("");
  const unitReversed = reversedInputString.match(/[^\d\s]+/)?.[0];
  if (!unitReversed) {
    throw new Error(`Could not determine unit: "${v}"`);
  }
  const unit = unitReversed.split("").reverse().join("");
  const numberPart = v.slice(0, -unit.length);
  const bareSiPrefixMultiplier = getSiPrefixMultiplier(unit);
  if (unitOfValue && bareSiPrefixMultiplier != null) {
    return {
      parsedUnit: null,
      unitOfValue,
      value: Number.parseFloat(numberPart) * bareSiPrefixMultiplier
    };
  }
  if (bareSiPrefixMultiplier != null && !unitMappingAndVariantSuffixes.has(unit)) {
    return {
      parsedUnit: null,
      unitOfValue: null,
      value: Number.parseFloat(numberPart) * bareSiPrefixMultiplier
    };
  }
  const { baseUnit, conversionFactor } = getBaseTscircuitUnit(unit);
  return {
    parsedUnit: unit,
    unitOfValue: baseUnit,
    value: conversionFactor * Number.parseFloat(numberPart)
  };
}
var SI_PREFIX_PATTERN = SI_PREFIXES.filter((prefix) => prefix !== "").sort((a, b) => b.length - a.length).map((prefix) => prefix.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|");
var SI_UNIT_PATTERN = new RegExp(`^([+-]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)(?:[eE][+-]?\\d+)?)(?:(${SI_PREFIX_PATTERN}))?$`);
var SI_PREFIXES2 = [
  { value: 1000000000000, symbol: "T" },
  { value: 1e9, symbol: "G" },
  { value: 1e6, symbol: "M" },
  { value: 1000, symbol: "k" },
  { value: 1, symbol: "" },
  { value: 0.001, symbol: "m" },
  { value: 0.000001, symbol: "µ" },
  { value: 0.000000001, symbol: "n" },
  { value: 0.000000000001, symbol: "p" }
];
var FALLBACK_PREFIX = SI_PREFIXES2[SI_PREFIXES2.length - 1];

// ../../../../tools/circuit-to-wokwi/node_modules/zod/v3/helpers/util.js
var util;
(function(util) {
  util.assertEqual = (_) => {};
  function assertIs(_arg) {}
  util.assertIs = assertIs;
  function assertNever(_x) {
    throw new Error;
  }
  util.assertNever = assertNever;
  util.arrayToEnum = (items) => {
    const obj = {};
    for (const item of items) {
      obj[item] = item;
    }
    return obj;
  };
  util.getValidEnumValues = (obj) => {
    const validKeys = util.objectKeys(obj).filter((k) => typeof obj[obj[k]] !== "number");
    const filtered = {};
    for (const k of validKeys) {
      filtered[k] = obj[k];
    }
    return util.objectValues(filtered);
  };
  util.objectValues = (obj) => {
    return util.objectKeys(obj).map(function(e) {
      return obj[e];
    });
  };
  util.objectKeys = typeof Object.keys === "function" ? (obj) => Object.keys(obj) : (object) => {
    const keys = [];
    for (const key in object) {
      if (Object.prototype.hasOwnProperty.call(object, key)) {
        keys.push(key);
      }
    }
    return keys;
  };
  util.find = (arr, checker) => {
    for (const item of arr) {
      if (checker(item))
        return item;
    }
    return;
  };
  util.isInteger = typeof Number.isInteger === "function" ? (val) => Number.isInteger(val) : (val) => typeof val === "number" && Number.isFinite(val) && Math.floor(val) === val;
  function joinValues(array, separator = " | ") {
    return array.map((val) => typeof val === "string" ? `'${val}'` : val).join(separator);
  }
  util.joinValues = joinValues;
  util.jsonStringifyReplacer = (_, value) => {
    if (typeof value === "bigint") {
      return value.toString();
    }
    return value;
  };
})(util || (util = {}));
var objectUtil;
(function(objectUtil) {
  objectUtil.mergeShapes = (first, second) => {
    return {
      ...first,
      ...second
    };
  };
})(objectUtil || (objectUtil = {}));
var ZodParsedType = util.arrayToEnum([
  "string",
  "nan",
  "number",
  "integer",
  "float",
  "boolean",
  "date",
  "bigint",
  "symbol",
  "function",
  "undefined",
  "null",
  "array",
  "object",
  "unknown",
  "promise",
  "void",
  "never",
  "map",
  "set"
]);
var getParsedType = (data) => {
  const t = typeof data;
  switch (t) {
    case "undefined":
      return ZodParsedType.undefined;
    case "string":
      return ZodParsedType.string;
    case "number":
      return Number.isNaN(data) ? ZodParsedType.nan : ZodParsedType.number;
    case "boolean":
      return ZodParsedType.boolean;
    case "function":
      return ZodParsedType.function;
    case "bigint":
      return ZodParsedType.bigint;
    case "symbol":
      return ZodParsedType.symbol;
    case "object":
      if (Array.isArray(data)) {
        return ZodParsedType.array;
      }
      if (data === null) {
        return ZodParsedType.null;
      }
      if (data.then && typeof data.then === "function" && data.catch && typeof data.catch === "function") {
        return ZodParsedType.promise;
      }
      if (typeof Map !== "undefined" && data instanceof Map) {
        return ZodParsedType.map;
      }
      if (typeof Set !== "undefined" && data instanceof Set) {
        return ZodParsedType.set;
      }
      if (typeof Date !== "undefined" && data instanceof Date) {
        return ZodParsedType.date;
      }
      return ZodParsedType.object;
    default:
      return ZodParsedType.unknown;
  }
};

// ../../../../tools/circuit-to-wokwi/node_modules/zod/v3/ZodError.js
var ZodIssueCode = util.arrayToEnum([
  "invalid_type",
  "invalid_literal",
  "custom",
  "invalid_union",
  "invalid_union_discriminator",
  "invalid_enum_value",
  "unrecognized_keys",
  "invalid_arguments",
  "invalid_return_type",
  "invalid_date",
  "invalid_string",
  "too_small",
  "too_big",
  "invalid_intersection_types",
  "not_multiple_of",
  "not_finite"
]);
class ZodError extends Error {
  get errors() {
    return this.issues;
  }
  constructor(issues) {
    super();
    this.issues = [];
    this.addIssue = (sub) => {
      this.issues = [...this.issues, sub];
    };
    this.addIssues = (subs = []) => {
      this.issues = [...this.issues, ...subs];
    };
    const actualProto = new.target.prototype;
    if (Object.setPrototypeOf) {
      Object.setPrototypeOf(this, actualProto);
    } else {
      this.__proto__ = actualProto;
    }
    this.name = "ZodError";
    this.issues = issues;
  }
  format(_mapper) {
    const mapper = _mapper || function(issue) {
      return issue.message;
    };
    const fieldErrors = { _errors: [] };
    const processError = (error) => {
      for (const issue of error.issues) {
        if (issue.code === "invalid_union") {
          issue.unionErrors.map(processError);
        } else if (issue.code === "invalid_return_type") {
          processError(issue.returnTypeError);
        } else if (issue.code === "invalid_arguments") {
          processError(issue.argumentsError);
        } else if (issue.path.length === 0) {
          fieldErrors._errors.push(mapper(issue));
        } else {
          let curr = fieldErrors;
          let i = 0;
          while (i < issue.path.length) {
            const el = issue.path[i];
            const terminal = i === issue.path.length - 1;
            if (!terminal) {
              curr[el] = curr[el] || { _errors: [] };
            } else {
              curr[el] = curr[el] || { _errors: [] };
              curr[el]._errors.push(mapper(issue));
            }
            curr = curr[el];
            i++;
          }
        }
      }
    };
    processError(this);
    return fieldErrors;
  }
  static assert(value) {
    if (!(value instanceof ZodError)) {
      throw new Error(`Not a ZodError: ${value}`);
    }
  }
  toString() {
    return this.message;
  }
  get message() {
    return JSON.stringify(this.issues, util.jsonStringifyReplacer, 2);
  }
  get isEmpty() {
    return this.issues.length === 0;
  }
  flatten(mapper = (issue) => issue.message) {
    const fieldErrors = {};
    const formErrors = [];
    for (const sub of this.issues) {
      if (sub.path.length > 0) {
        const firstEl = sub.path[0];
        fieldErrors[firstEl] = fieldErrors[firstEl] || [];
        fieldErrors[firstEl].push(mapper(sub));
      } else {
        formErrors.push(mapper(sub));
      }
    }
    return { formErrors, fieldErrors };
  }
  get formErrors() {
    return this.flatten();
  }
}
ZodError.create = (issues) => {
  const error = new ZodError(issues);
  return error;
};

// ../../../../tools/circuit-to-wokwi/node_modules/zod/v3/locales/en.js
var errorMap = (issue, _ctx) => {
  let message;
  switch (issue.code) {
    case ZodIssueCode.invalid_type:
      if (issue.received === ZodParsedType.undefined) {
        message = "Required";
      } else {
        message = `Expected ${issue.expected}, received ${issue.received}`;
      }
      break;
    case ZodIssueCode.invalid_literal:
      message = `Invalid literal value, expected ${JSON.stringify(issue.expected, util.jsonStringifyReplacer)}`;
      break;
    case ZodIssueCode.unrecognized_keys:
      message = `Unrecognized key(s) in object: ${util.joinValues(issue.keys, ", ")}`;
      break;
    case ZodIssueCode.invalid_union:
      message = `Invalid input`;
      break;
    case ZodIssueCode.invalid_union_discriminator:
      message = `Invalid discriminator value. Expected ${util.joinValues(issue.options)}`;
      break;
    case ZodIssueCode.invalid_enum_value:
      message = `Invalid enum value. Expected ${util.joinValues(issue.options)}, received '${issue.received}'`;
      break;
    case ZodIssueCode.invalid_arguments:
      message = `Invalid function arguments`;
      break;
    case ZodIssueCode.invalid_return_type:
      message = `Invalid function return type`;
      break;
    case ZodIssueCode.invalid_date:
      message = `Invalid date`;
      break;
    case ZodIssueCode.invalid_string:
      if (typeof issue.validation === "object") {
        if ("includes" in issue.validation) {
          message = `Invalid input: must include "${issue.validation.includes}"`;
          if (typeof issue.validation.position === "number") {
            message = `${message} at one or more positions greater than or equal to ${issue.validation.position}`;
          }
        } else if ("startsWith" in issue.validation) {
          message = `Invalid input: must start with "${issue.validation.startsWith}"`;
        } else if ("endsWith" in issue.validation) {
          message = `Invalid input: must end with "${issue.validation.endsWith}"`;
        } else {
          util.assertNever(issue.validation);
        }
      } else if (issue.validation !== "regex") {
        message = `Invalid ${issue.validation}`;
      } else {
        message = "Invalid";
      }
      break;
    case ZodIssueCode.too_small:
      if (issue.type === "array")
        message = `Array must contain ${issue.exact ? "exactly" : issue.inclusive ? `at least` : `more than`} ${issue.minimum} element(s)`;
      else if (issue.type === "string")
        message = `String must contain ${issue.exact ? "exactly" : issue.inclusive ? `at least` : `over`} ${issue.minimum} character(s)`;
      else if (issue.type === "number")
        message = `Number must be ${issue.exact ? `exactly equal to ` : issue.inclusive ? `greater than or equal to ` : `greater than `}${issue.minimum}`;
      else if (issue.type === "bigint")
        message = `Number must be ${issue.exact ? `exactly equal to ` : issue.inclusive ? `greater than or equal to ` : `greater than `}${issue.minimum}`;
      else if (issue.type === "date")
        message = `Date must be ${issue.exact ? `exactly equal to ` : issue.inclusive ? `greater than or equal to ` : `greater than `}${new Date(Number(issue.minimum))}`;
      else
        message = "Invalid input";
      break;
    case ZodIssueCode.too_big:
      if (issue.type === "array")
        message = `Array must contain ${issue.exact ? `exactly` : issue.inclusive ? `at most` : `less than`} ${issue.maximum} element(s)`;
      else if (issue.type === "string")
        message = `String must contain ${issue.exact ? `exactly` : issue.inclusive ? `at most` : `under`} ${issue.maximum} character(s)`;
      else if (issue.type === "number")
        message = `Number must be ${issue.exact ? `exactly` : issue.inclusive ? `less than or equal to` : `less than`} ${issue.maximum}`;
      else if (issue.type === "bigint")
        message = `BigInt must be ${issue.exact ? `exactly` : issue.inclusive ? `less than or equal to` : `less than`} ${issue.maximum}`;
      else if (issue.type === "date")
        message = `Date must be ${issue.exact ? `exactly` : issue.inclusive ? `smaller than or equal to` : `smaller than`} ${new Date(Number(issue.maximum))}`;
      else
        message = "Invalid input";
      break;
    case ZodIssueCode.custom:
      message = `Invalid input`;
      break;
    case ZodIssueCode.invalid_intersection_types:
      message = `Intersection results could not be merged`;
      break;
    case ZodIssueCode.not_multiple_of:
      message = `Number must be a multiple of ${issue.multipleOf}`;
      break;
    case ZodIssueCode.not_finite:
      message = "Number must be finite";
      break;
    default:
      message = _ctx.defaultError;
      util.assertNever(issue);
  }
  return { message };
};
var en_default = errorMap;

// ../../../../tools/circuit-to-wokwi/node_modules/zod/v3/errors.js
var overrideErrorMap = en_default;
function getErrorMap() {
  return overrideErrorMap;
}

// ../../../../tools/circuit-to-wokwi/node_modules/zod/v3/helpers/parseUtil.js
var makeIssue = (params) => {
  const { data, path, errorMaps, issueData } = params;
  const fullPath = [...path, ...issueData.path || []];
  const fullIssue = {
    ...issueData,
    path: fullPath
  };
  if (issueData.message !== undefined) {
    return {
      ...issueData,
      path: fullPath,
      message: issueData.message
    };
  }
  let errorMessage = "";
  const maps = errorMaps.filter((m) => !!m).slice().reverse();
  for (const map of maps) {
    errorMessage = map(fullIssue, { data, defaultError: errorMessage }).message;
  }
  return {
    ...issueData,
    path: fullPath,
    message: errorMessage
  };
};
function addIssueToContext(ctx, issueData) {
  const overrideMap = getErrorMap();
  const issue = makeIssue({
    issueData,
    data: ctx.data,
    path: ctx.path,
    errorMaps: [
      ctx.common.contextualErrorMap,
      ctx.schemaErrorMap,
      overrideMap,
      overrideMap === en_default ? undefined : en_default
    ].filter((x) => !!x)
  });
  ctx.common.issues.push(issue);
}

class ParseStatus {
  constructor() {
    this.value = "valid";
  }
  dirty() {
    if (this.value === "valid")
      this.value = "dirty";
  }
  abort() {
    if (this.value !== "aborted")
      this.value = "aborted";
  }
  static mergeArray(status, results) {
    const arrayValue = [];
    for (const s of results) {
      if (s.status === "aborted")
        return INVALID;
      if (s.status === "dirty")
        status.dirty();
      arrayValue.push(s.value);
    }
    return { status: status.value, value: arrayValue };
  }
  static async mergeObjectAsync(status, pairs) {
    const syncPairs = [];
    for (const pair of pairs) {
      const key = await pair.key;
      const value = await pair.value;
      syncPairs.push({
        key,
        value
      });
    }
    return ParseStatus.mergeObjectSync(status, syncPairs);
  }
  static mergeObjectSync(status, pairs) {
    const finalObject = {};
    for (const pair of pairs) {
      const { key, value } = pair;
      if (key.status === "aborted")
        return INVALID;
      if (value.status === "aborted")
        return INVALID;
      if (key.status === "dirty")
        status.dirty();
      if (value.status === "dirty")
        status.dirty();
      if (key.value !== "__proto__" && (typeof value.value !== "undefined" || pair.alwaysSet)) {
        finalObject[key.value] = value.value;
      }
    }
    return { status: status.value, value: finalObject };
  }
}
var INVALID = Object.freeze({
  status: "aborted"
});
var DIRTY = (value) => ({ status: "dirty", value });
var OK = (value) => ({ status: "valid", value });
var isAborted = (x) => x.status === "aborted";
var isDirty = (x) => x.status === "dirty";
var isValid = (x) => x.status === "valid";
var isAsync = (x) => typeof Promise !== "undefined" && x instanceof Promise;

// ../../../../tools/circuit-to-wokwi/node_modules/zod/v3/helpers/errorUtil.js
var errorUtil;
(function(errorUtil) {
  errorUtil.errToObj = (message) => typeof message === "string" ? { message } : message || {};
  errorUtil.toString = (message) => typeof message === "string" ? message : message?.message;
})(errorUtil || (errorUtil = {}));

// ../../../../tools/circuit-to-wokwi/node_modules/zod/v3/types.js
class ParseInputLazyPath {
  constructor(parent, value, path, key) {
    this._cachedPath = [];
    this.parent = parent;
    this.data = value;
    this._path = path;
    this._key = key;
  }
  get path() {
    if (!this._cachedPath.length) {
      if (Array.isArray(this._key)) {
        this._cachedPath.push(...this._path, ...this._key);
      } else {
        this._cachedPath.push(...this._path, this._key);
      }
    }
    return this._cachedPath;
  }
}
var handleResult = (ctx, result) => {
  if (isValid(result)) {
    return { success: true, data: result.value };
  } else {
    if (!ctx.common.issues.length) {
      throw new Error("Validation failed but no issues detected.");
    }
    return {
      success: false,
      get error() {
        if (this._error)
          return this._error;
        const error = new ZodError(ctx.common.issues);
        this._error = error;
        return this._error;
      }
    };
  }
};
function processCreateParams(params) {
  if (!params)
    return {};
  const { errorMap, invalid_type_error, required_error, description } = params;
  if (errorMap && (invalid_type_error || required_error)) {
    throw new Error(`Can't use "invalid_type_error" or "required_error" in conjunction with custom error map.`);
  }
  if (errorMap)
    return { errorMap, description };
  const customMap = (iss, ctx) => {
    const { message } = params;
    if (iss.code === "invalid_enum_value") {
      return { message: message ?? ctx.defaultError };
    }
    if (typeof ctx.data === "undefined") {
      return { message: message ?? required_error ?? ctx.defaultError };
    }
    if (iss.code !== "invalid_type")
      return { message: ctx.defaultError };
    return { message: message ?? invalid_type_error ?? ctx.defaultError };
  };
  return { errorMap: customMap, description };
}

class ZodType {
  get description() {
    return this._def.description;
  }
  _getType(input) {
    return getParsedType(input.data);
  }
  _getOrReturnCtx(input, ctx) {
    return ctx || {
      common: input.parent.common,
      data: input.data,
      parsedType: getParsedType(input.data),
      schemaErrorMap: this._def.errorMap,
      path: input.path,
      parent: input.parent
    };
  }
  _processInputParams(input) {
    return {
      status: new ParseStatus,
      ctx: {
        common: input.parent.common,
        data: input.data,
        parsedType: getParsedType(input.data),
        schemaErrorMap: this._def.errorMap,
        path: input.path,
        parent: input.parent
      }
    };
  }
  _parseSync(input) {
    const result = this._parse(input);
    if (isAsync(result)) {
      throw new Error("Synchronous parse encountered promise.");
    }
    return result;
  }
  _parseAsync(input) {
    const result = this._parse(input);
    return Promise.resolve(result);
  }
  parse(data, params) {
    const result = this.safeParse(data, params);
    if (result.success)
      return result.data;
    throw result.error;
  }
  safeParse(data, params) {
    const ctx = {
      common: {
        issues: [],
        async: params?.async ?? false,
        contextualErrorMap: params?.errorMap
      },
      path: params?.path || [],
      schemaErrorMap: this._def.errorMap,
      parent: null,
      data,
      parsedType: getParsedType(data)
    };
    const result = this._parseSync({ data, path: ctx.path, parent: ctx });
    return handleResult(ctx, result);
  }
  "~validate"(data) {
    const ctx = {
      common: {
        issues: [],
        async: !!this["~standard"].async
      },
      path: [],
      schemaErrorMap: this._def.errorMap,
      parent: null,
      data,
      parsedType: getParsedType(data)
    };
    if (!this["~standard"].async) {
      try {
        const result = this._parseSync({ data, path: [], parent: ctx });
        return isValid(result) ? {
          value: result.value
        } : {
          issues: ctx.common.issues
        };
      } catch (err) {
        if (err?.message?.toLowerCase()?.includes("encountered")) {
          this["~standard"].async = true;
        }
        ctx.common = {
          issues: [],
          async: true
        };
      }
    }
    return this._parseAsync({ data, path: [], parent: ctx }).then((result) => isValid(result) ? {
      value: result.value
    } : {
      issues: ctx.common.issues
    });
  }
  async parseAsync(data, params) {
    const result = await this.safeParseAsync(data, params);
    if (result.success)
      return result.data;
    throw result.error;
  }
  async safeParseAsync(data, params) {
    const ctx = {
      common: {
        issues: [],
        contextualErrorMap: params?.errorMap,
        async: true
      },
      path: params?.path || [],
      schemaErrorMap: this._def.errorMap,
      parent: null,
      data,
      parsedType: getParsedType(data)
    };
    const maybeAsyncResult = this._parse({ data, path: ctx.path, parent: ctx });
    const result = await (isAsync(maybeAsyncResult) ? maybeAsyncResult : Promise.resolve(maybeAsyncResult));
    return handleResult(ctx, result);
  }
  refine(check, message) {
    const getIssueProperties = (val) => {
      if (typeof message === "string" || typeof message === "undefined") {
        return { message };
      } else if (typeof message === "function") {
        return message(val);
      } else {
        return message;
      }
    };
    return this._refinement((val, ctx) => {
      const result = check(val);
      const setError = () => ctx.addIssue({
        code: ZodIssueCode.custom,
        ...getIssueProperties(val)
      });
      if (typeof Promise !== "undefined" && result instanceof Promise) {
        return result.then((data) => {
          if (!data) {
            setError();
            return false;
          } else {
            return true;
          }
        });
      }
      if (!result) {
        setError();
        return false;
      } else {
        return true;
      }
    });
  }
  refinement(check, refinementData) {
    return this._refinement((val, ctx) => {
      if (!check(val)) {
        ctx.addIssue(typeof refinementData === "function" ? refinementData(val, ctx) : refinementData);
        return false;
      } else {
        return true;
      }
    });
  }
  _refinement(refinement) {
    return new ZodEffects({
      schema: this,
      typeName: ZodFirstPartyTypeKind.ZodEffects,
      effect: { type: "refinement", refinement }
    });
  }
  superRefine(refinement) {
    return this._refinement(refinement);
  }
  constructor(def) {
    this.spa = this.safeParseAsync;
    this._def = def;
    this.parse = this.parse.bind(this);
    this.safeParse = this.safeParse.bind(this);
    this.parseAsync = this.parseAsync.bind(this);
    this.safeParseAsync = this.safeParseAsync.bind(this);
    this.spa = this.spa.bind(this);
    this.refine = this.refine.bind(this);
    this.refinement = this.refinement.bind(this);
    this.superRefine = this.superRefine.bind(this);
    this.optional = this.optional.bind(this);
    this.nullable = this.nullable.bind(this);
    this.nullish = this.nullish.bind(this);
    this.array = this.array.bind(this);
    this.promise = this.promise.bind(this);
    this.or = this.or.bind(this);
    this.and = this.and.bind(this);
    this.transform = this.transform.bind(this);
    this.brand = this.brand.bind(this);
    this.default = this.default.bind(this);
    this.catch = this.catch.bind(this);
    this.describe = this.describe.bind(this);
    this.pipe = this.pipe.bind(this);
    this.readonly = this.readonly.bind(this);
    this.isNullable = this.isNullable.bind(this);
    this.isOptional = this.isOptional.bind(this);
    this["~standard"] = {
      version: 1,
      vendor: "zod",
      validate: (data) => this["~validate"](data)
    };
  }
  optional() {
    return ZodOptional.create(this, this._def);
  }
  nullable() {
    return ZodNullable.create(this, this._def);
  }
  nullish() {
    return this.nullable().optional();
  }
  array() {
    return ZodArray.create(this);
  }
  promise() {
    return ZodPromise.create(this, this._def);
  }
  or(option) {
    return ZodUnion.create([this, option], this._def);
  }
  and(incoming) {
    return ZodIntersection.create(this, incoming, this._def);
  }
  transform(transform) {
    return new ZodEffects({
      ...processCreateParams(this._def),
      schema: this,
      typeName: ZodFirstPartyTypeKind.ZodEffects,
      effect: { type: "transform", transform }
    });
  }
  default(def) {
    const defaultValueFunc = typeof def === "function" ? def : () => def;
    return new ZodDefault({
      ...processCreateParams(this._def),
      innerType: this,
      defaultValue: defaultValueFunc,
      typeName: ZodFirstPartyTypeKind.ZodDefault
    });
  }
  brand() {
    return new ZodBranded({
      typeName: ZodFirstPartyTypeKind.ZodBranded,
      type: this,
      ...processCreateParams(this._def)
    });
  }
  catch(def) {
    const catchValueFunc = typeof def === "function" ? def : () => def;
    return new ZodCatch({
      ...processCreateParams(this._def),
      innerType: this,
      catchValue: catchValueFunc,
      typeName: ZodFirstPartyTypeKind.ZodCatch
    });
  }
  describe(description) {
    const This = this.constructor;
    return new This({
      ...this._def,
      description
    });
  }
  pipe(target) {
    return ZodPipeline.create(this, target);
  }
  readonly() {
    return ZodReadonly.create(this);
  }
  isOptional() {
    return this.safeParse(undefined).success;
  }
  isNullable() {
    return this.safeParse(null).success;
  }
}
var cuidRegex = /^c[^\s-]{8,}$/i;
var cuid2Regex = /^[0-9a-z]+$/;
var ulidRegex = /^[0-9A-HJKMNP-TV-Z]{26}$/i;
var uuidRegex = /^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$/i;
var nanoidRegex = /^[a-z0-9_-]{21}$/i;
var jwtRegex = /^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$/;
var durationRegex = /^[-+]?P(?!$)(?:(?:[-+]?\d+Y)|(?:[-+]?\d+[.,]\d+Y$))?(?:(?:[-+]?\d+M)|(?:[-+]?\d+[.,]\d+M$))?(?:(?:[-+]?\d+W)|(?:[-+]?\d+[.,]\d+W$))?(?:(?:[-+]?\d+D)|(?:[-+]?\d+[.,]\d+D$))?(?:T(?=[\d+-])(?:(?:[-+]?\d+H)|(?:[-+]?\d+[.,]\d+H$))?(?:(?:[-+]?\d+M)|(?:[-+]?\d+[.,]\d+M$))?(?:[-+]?\d+(?:[.,]\d+)?S)?)??$/;
var emailRegex = /^(?!\.)(?!.*\.\.)([A-Z0-9_'+\-\.]*)[A-Z0-9_+-]@([A-Z0-9][A-Z0-9\-]*\.)+[A-Z]{2,}$/i;
var _emojiRegex = `^(\\p{Extended_Pictographic}|\\p{Emoji_Component})+$`;
var emojiRegex;
var ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])$/;
var ipv4CidrRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\/(3[0-2]|[12]?[0-9])$/;
var ipv6Regex = /^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$/;
var ipv6CidrRegex = /^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\/(12[0-8]|1[01][0-9]|[1-9]?[0-9])$/;
var base64Regex = /^([0-9a-zA-Z+/]{4})*(([0-9a-zA-Z+/]{2}==)|([0-9a-zA-Z+/]{3}=))?$/;
var base64urlRegex = /^([0-9a-zA-Z-_]{4})*(([0-9a-zA-Z-_]{2}(==)?)|([0-9a-zA-Z-_]{3}(=)?))?$/;
var dateRegexSource = `((\\d\\d[2468][048]|\\d\\d[13579][26]|\\d\\d0[48]|[02468][048]00|[13579][26]00)-02-29|\\d{4}-((0[13578]|1[02])-(0[1-9]|[12]\\d|3[01])|(0[469]|11)-(0[1-9]|[12]\\d|30)|(02)-(0[1-9]|1\\d|2[0-8])))`;
var dateRegex = new RegExp(`^${dateRegexSource}$`);
function timeRegexSource(args) {
  let secondsRegexSource = `[0-5]\\d`;
  if (args.precision) {
    secondsRegexSource = `${secondsRegexSource}\\.\\d{${args.precision}}`;
  } else if (args.precision == null) {
    secondsRegexSource = `${secondsRegexSource}(\\.\\d+)?`;
  }
  const secondsQuantifier = args.precision ? "+" : "?";
  return `([01]\\d|2[0-3]):[0-5]\\d(:${secondsRegexSource})${secondsQuantifier}`;
}
function timeRegex(args) {
  return new RegExp(`^${timeRegexSource(args)}$`);
}
function datetimeRegex(args) {
  let regex = `${dateRegexSource}T${timeRegexSource(args)}`;
  const opts = [];
  opts.push(args.local ? `Z?` : `Z`);
  if (args.offset)
    opts.push(`([+-]\\d{2}:?\\d{2})`);
  regex = `${regex}(${opts.join("|")})`;
  return new RegExp(`^${regex}$`);
}
function isValidIP(ip, version) {
  if ((version === "v4" || !version) && ipv4Regex.test(ip)) {
    return true;
  }
  if ((version === "v6" || !version) && ipv6Regex.test(ip)) {
    return true;
  }
  return false;
}
function isValidJWT(jwt, alg) {
  if (!jwtRegex.test(jwt))
    return false;
  try {
    const [header] = jwt.split(".");
    if (!header)
      return false;
    const base64 = header.replace(/-/g, "+").replace(/_/g, "/").padEnd(header.length + (4 - header.length % 4) % 4, "=");
    const decoded = JSON.parse(atob(base64));
    if (typeof decoded !== "object" || decoded === null)
      return false;
    if ("typ" in decoded && decoded?.typ !== "JWT")
      return false;
    if (!decoded.alg)
      return false;
    if (alg && decoded.alg !== alg)
      return false;
    return true;
  } catch {
    return false;
  }
}
function isValidCidr(ip, version) {
  if ((version === "v4" || !version) && ipv4CidrRegex.test(ip)) {
    return true;
  }
  if ((version === "v6" || !version) && ipv6CidrRegex.test(ip)) {
    return true;
  }
  return false;
}

class ZodString extends ZodType {
  _parse(input) {
    if (this._def.coerce) {
      input.data = String(input.data);
    }
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.string) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.string,
        received: ctx.parsedType
      });
      return INVALID;
    }
    const status = new ParseStatus;
    let ctx = undefined;
    for (const check of this._def.checks) {
      if (check.kind === "min") {
        if (input.data.length < check.value) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_small,
            minimum: check.value,
            type: "string",
            inclusive: true,
            exact: false,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "max") {
        if (input.data.length > check.value) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_big,
            maximum: check.value,
            type: "string",
            inclusive: true,
            exact: false,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "length") {
        const tooBig = input.data.length > check.value;
        const tooSmall = input.data.length < check.value;
        if (tooBig || tooSmall) {
          ctx = this._getOrReturnCtx(input, ctx);
          if (tooBig) {
            addIssueToContext(ctx, {
              code: ZodIssueCode.too_big,
              maximum: check.value,
              type: "string",
              inclusive: true,
              exact: true,
              message: check.message
            });
          } else if (tooSmall) {
            addIssueToContext(ctx, {
              code: ZodIssueCode.too_small,
              minimum: check.value,
              type: "string",
              inclusive: true,
              exact: true,
              message: check.message
            });
          }
          status.dirty();
        }
      } else if (check.kind === "email") {
        if (!emailRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "email",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "emoji") {
        if (!emojiRegex) {
          emojiRegex = new RegExp(_emojiRegex, "u");
        }
        if (!emojiRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "emoji",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "uuid") {
        if (!uuidRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "uuid",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "nanoid") {
        if (!nanoidRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "nanoid",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "cuid") {
        if (!cuidRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "cuid",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "cuid2") {
        if (!cuid2Regex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "cuid2",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "ulid") {
        if (!ulidRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "ulid",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "url") {
        try {
          new URL(input.data);
        } catch {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "url",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "regex") {
        check.regex.lastIndex = 0;
        const testResult = check.regex.test(input.data);
        if (!testResult) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "regex",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "trim") {
        input.data = input.data.trim();
      } else if (check.kind === "includes") {
        if (!input.data.includes(check.value, check.position)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.invalid_string,
            validation: { includes: check.value, position: check.position },
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "toLowerCase") {
        input.data = input.data.toLowerCase();
      } else if (check.kind === "toUpperCase") {
        input.data = input.data.toUpperCase();
      } else if (check.kind === "startsWith") {
        if (!input.data.startsWith(check.value)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.invalid_string,
            validation: { startsWith: check.value },
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "endsWith") {
        if (!input.data.endsWith(check.value)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.invalid_string,
            validation: { endsWith: check.value },
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "datetime") {
        const regex = datetimeRegex(check);
        if (!regex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.invalid_string,
            validation: "datetime",
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "date") {
        const regex = dateRegex;
        if (!regex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.invalid_string,
            validation: "date",
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "time") {
        const regex = timeRegex(check);
        if (!regex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.invalid_string,
            validation: "time",
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "duration") {
        if (!durationRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "duration",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "ip") {
        if (!isValidIP(input.data, check.version)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "ip",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "jwt") {
        if (!isValidJWT(input.data, check.alg)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "jwt",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "cidr") {
        if (!isValidCidr(input.data, check.version)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "cidr",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "base64") {
        if (!base64Regex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "base64",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "base64url") {
        if (!base64urlRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "base64url",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else {
        util.assertNever(check);
      }
    }
    return { status: status.value, value: input.data };
  }
  _regex(regex, validation, message) {
    return this.refinement((data) => regex.test(data), {
      validation,
      code: ZodIssueCode.invalid_string,
      ...errorUtil.errToObj(message)
    });
  }
  _addCheck(check) {
    return new ZodString({
      ...this._def,
      checks: [...this._def.checks, check]
    });
  }
  email(message) {
    return this._addCheck({ kind: "email", ...errorUtil.errToObj(message) });
  }
  url(message) {
    return this._addCheck({ kind: "url", ...errorUtil.errToObj(message) });
  }
  emoji(message) {
    return this._addCheck({ kind: "emoji", ...errorUtil.errToObj(message) });
  }
  uuid(message) {
    return this._addCheck({ kind: "uuid", ...errorUtil.errToObj(message) });
  }
  nanoid(message) {
    return this._addCheck({ kind: "nanoid", ...errorUtil.errToObj(message) });
  }
  cuid(message) {
    return this._addCheck({ kind: "cuid", ...errorUtil.errToObj(message) });
  }
  cuid2(message) {
    return this._addCheck({ kind: "cuid2", ...errorUtil.errToObj(message) });
  }
  ulid(message) {
    return this._addCheck({ kind: "ulid", ...errorUtil.errToObj(message) });
  }
  base64(message) {
    return this._addCheck({ kind: "base64", ...errorUtil.errToObj(message) });
  }
  base64url(message) {
    return this._addCheck({
      kind: "base64url",
      ...errorUtil.errToObj(message)
    });
  }
  jwt(options) {
    return this._addCheck({ kind: "jwt", ...errorUtil.errToObj(options) });
  }
  ip(options) {
    return this._addCheck({ kind: "ip", ...errorUtil.errToObj(options) });
  }
  cidr(options) {
    return this._addCheck({ kind: "cidr", ...errorUtil.errToObj(options) });
  }
  datetime(options) {
    if (typeof options === "string") {
      return this._addCheck({
        kind: "datetime",
        precision: null,
        offset: false,
        local: false,
        message: options
      });
    }
    return this._addCheck({
      kind: "datetime",
      precision: typeof options?.precision === "undefined" ? null : options?.precision,
      offset: options?.offset ?? false,
      local: options?.local ?? false,
      ...errorUtil.errToObj(options?.message)
    });
  }
  date(message) {
    return this._addCheck({ kind: "date", message });
  }
  time(options) {
    if (typeof options === "string") {
      return this._addCheck({
        kind: "time",
        precision: null,
        message: options
      });
    }
    return this._addCheck({
      kind: "time",
      precision: typeof options?.precision === "undefined" ? null : options?.precision,
      ...errorUtil.errToObj(options?.message)
    });
  }
  duration(message) {
    return this._addCheck({ kind: "duration", ...errorUtil.errToObj(message) });
  }
  regex(regex, message) {
    return this._addCheck({
      kind: "regex",
      regex,
      ...errorUtil.errToObj(message)
    });
  }
  includes(value, options) {
    return this._addCheck({
      kind: "includes",
      value,
      position: options?.position,
      ...errorUtil.errToObj(options?.message)
    });
  }
  startsWith(value, message) {
    return this._addCheck({
      kind: "startsWith",
      value,
      ...errorUtil.errToObj(message)
    });
  }
  endsWith(value, message) {
    return this._addCheck({
      kind: "endsWith",
      value,
      ...errorUtil.errToObj(message)
    });
  }
  min(minLength, message) {
    return this._addCheck({
      kind: "min",
      value: minLength,
      ...errorUtil.errToObj(message)
    });
  }
  max(maxLength, message) {
    return this._addCheck({
      kind: "max",
      value: maxLength,
      ...errorUtil.errToObj(message)
    });
  }
  length(len, message) {
    return this._addCheck({
      kind: "length",
      value: len,
      ...errorUtil.errToObj(message)
    });
  }
  nonempty(message) {
    return this.min(1, errorUtil.errToObj(message));
  }
  trim() {
    return new ZodString({
      ...this._def,
      checks: [...this._def.checks, { kind: "trim" }]
    });
  }
  toLowerCase() {
    return new ZodString({
      ...this._def,
      checks: [...this._def.checks, { kind: "toLowerCase" }]
    });
  }
  toUpperCase() {
    return new ZodString({
      ...this._def,
      checks: [...this._def.checks, { kind: "toUpperCase" }]
    });
  }
  get isDatetime() {
    return !!this._def.checks.find((ch) => ch.kind === "datetime");
  }
  get isDate() {
    return !!this._def.checks.find((ch) => ch.kind === "date");
  }
  get isTime() {
    return !!this._def.checks.find((ch) => ch.kind === "time");
  }
  get isDuration() {
    return !!this._def.checks.find((ch) => ch.kind === "duration");
  }
  get isEmail() {
    return !!this._def.checks.find((ch) => ch.kind === "email");
  }
  get isURL() {
    return !!this._def.checks.find((ch) => ch.kind === "url");
  }
  get isEmoji() {
    return !!this._def.checks.find((ch) => ch.kind === "emoji");
  }
  get isUUID() {
    return !!this._def.checks.find((ch) => ch.kind === "uuid");
  }
  get isNANOID() {
    return !!this._def.checks.find((ch) => ch.kind === "nanoid");
  }
  get isCUID() {
    return !!this._def.checks.find((ch) => ch.kind === "cuid");
  }
  get isCUID2() {
    return !!this._def.checks.find((ch) => ch.kind === "cuid2");
  }
  get isULID() {
    return !!this._def.checks.find((ch) => ch.kind === "ulid");
  }
  get isIP() {
    return !!this._def.checks.find((ch) => ch.kind === "ip");
  }
  get isCIDR() {
    return !!this._def.checks.find((ch) => ch.kind === "cidr");
  }
  get isBase64() {
    return !!this._def.checks.find((ch) => ch.kind === "base64");
  }
  get isBase64url() {
    return !!this._def.checks.find((ch) => ch.kind === "base64url");
  }
  get minLength() {
    let min = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "min") {
        if (min === null || ch.value > min)
          min = ch.value;
      }
    }
    return min;
  }
  get maxLength() {
    let max = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "max") {
        if (max === null || ch.value < max)
          max = ch.value;
      }
    }
    return max;
  }
}
ZodString.create = (params) => {
  return new ZodString({
    checks: [],
    typeName: ZodFirstPartyTypeKind.ZodString,
    coerce: params?.coerce ?? false,
    ...processCreateParams(params)
  });
};
function floatSafeRemainder(val, step) {
  const valDecCount = (val.toString().split(".")[1] || "").length;
  const stepDecCount = (step.toString().split(".")[1] || "").length;
  const decCount = valDecCount > stepDecCount ? valDecCount : stepDecCount;
  const valInt = Number.parseInt(val.toFixed(decCount).replace(".", ""));
  const stepInt = Number.parseInt(step.toFixed(decCount).replace(".", ""));
  return valInt % stepInt / 10 ** decCount;
}

class ZodNumber extends ZodType {
  constructor() {
    super(...arguments);
    this.min = this.gte;
    this.max = this.lte;
    this.step = this.multipleOf;
  }
  _parse(input) {
    if (this._def.coerce) {
      input.data = Number(input.data);
    }
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.number) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.number,
        received: ctx.parsedType
      });
      return INVALID;
    }
    let ctx = undefined;
    const status = new ParseStatus;
    for (const check of this._def.checks) {
      if (check.kind === "int") {
        if (!util.isInteger(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.invalid_type,
            expected: "integer",
            received: "float",
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "min") {
        const tooSmall = check.inclusive ? input.data < check.value : input.data <= check.value;
        if (tooSmall) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_small,
            minimum: check.value,
            type: "number",
            inclusive: check.inclusive,
            exact: false,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "max") {
        const tooBig = check.inclusive ? input.data > check.value : input.data >= check.value;
        if (tooBig) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_big,
            maximum: check.value,
            type: "number",
            inclusive: check.inclusive,
            exact: false,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "multipleOf") {
        if (floatSafeRemainder(input.data, check.value) !== 0) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.not_multiple_of,
            multipleOf: check.value,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "finite") {
        if (!Number.isFinite(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.not_finite,
            message: check.message
          });
          status.dirty();
        }
      } else {
        util.assertNever(check);
      }
    }
    return { status: status.value, value: input.data };
  }
  gte(value, message) {
    return this.setLimit("min", value, true, errorUtil.toString(message));
  }
  gt(value, message) {
    return this.setLimit("min", value, false, errorUtil.toString(message));
  }
  lte(value, message) {
    return this.setLimit("max", value, true, errorUtil.toString(message));
  }
  lt(value, message) {
    return this.setLimit("max", value, false, errorUtil.toString(message));
  }
  setLimit(kind, value, inclusive, message) {
    return new ZodNumber({
      ...this._def,
      checks: [
        ...this._def.checks,
        {
          kind,
          value,
          inclusive,
          message: errorUtil.toString(message)
        }
      ]
    });
  }
  _addCheck(check) {
    return new ZodNumber({
      ...this._def,
      checks: [...this._def.checks, check]
    });
  }
  int(message) {
    return this._addCheck({
      kind: "int",
      message: errorUtil.toString(message)
    });
  }
  positive(message) {
    return this._addCheck({
      kind: "min",
      value: 0,
      inclusive: false,
      message: errorUtil.toString(message)
    });
  }
  negative(message) {
    return this._addCheck({
      kind: "max",
      value: 0,
      inclusive: false,
      message: errorUtil.toString(message)
    });
  }
  nonpositive(message) {
    return this._addCheck({
      kind: "max",
      value: 0,
      inclusive: true,
      message: errorUtil.toString(message)
    });
  }
  nonnegative(message) {
    return this._addCheck({
      kind: "min",
      value: 0,
      inclusive: true,
      message: errorUtil.toString(message)
    });
  }
  multipleOf(value, message) {
    return this._addCheck({
      kind: "multipleOf",
      value,
      message: errorUtil.toString(message)
    });
  }
  finite(message) {
    return this._addCheck({
      kind: "finite",
      message: errorUtil.toString(message)
    });
  }
  safe(message) {
    return this._addCheck({
      kind: "min",
      inclusive: true,
      value: Number.MIN_SAFE_INTEGER,
      message: errorUtil.toString(message)
    })._addCheck({
      kind: "max",
      inclusive: true,
      value: Number.MAX_SAFE_INTEGER,
      message: errorUtil.toString(message)
    });
  }
  get minValue() {
    let min = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "min") {
        if (min === null || ch.value > min)
          min = ch.value;
      }
    }
    return min;
  }
  get maxValue() {
    let max = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "max") {
        if (max === null || ch.value < max)
          max = ch.value;
      }
    }
    return max;
  }
  get isInt() {
    return !!this._def.checks.find((ch) => ch.kind === "int" || ch.kind === "multipleOf" && util.isInteger(ch.value));
  }
  get isFinite() {
    let max = null;
    let min = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "finite" || ch.kind === "int" || ch.kind === "multipleOf") {
        return true;
      } else if (ch.kind === "min") {
        if (min === null || ch.value > min)
          min = ch.value;
      } else if (ch.kind === "max") {
        if (max === null || ch.value < max)
          max = ch.value;
      }
    }
    return Number.isFinite(min) && Number.isFinite(max);
  }
}
ZodNumber.create = (params) => {
  return new ZodNumber({
    checks: [],
    typeName: ZodFirstPartyTypeKind.ZodNumber,
    coerce: params?.coerce || false,
    ...processCreateParams(params)
  });
};

class ZodBigInt extends ZodType {
  constructor() {
    super(...arguments);
    this.min = this.gte;
    this.max = this.lte;
  }
  _parse(input) {
    if (this._def.coerce) {
      try {
        input.data = BigInt(input.data);
      } catch {
        return this._getInvalidInput(input);
      }
    }
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.bigint) {
      return this._getInvalidInput(input);
    }
    let ctx = undefined;
    const status = new ParseStatus;
    for (const check of this._def.checks) {
      if (check.kind === "min") {
        const tooSmall = check.inclusive ? input.data < check.value : input.data <= check.value;
        if (tooSmall) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_small,
            type: "bigint",
            minimum: check.value,
            inclusive: check.inclusive,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "max") {
        const tooBig = check.inclusive ? input.data > check.value : input.data >= check.value;
        if (tooBig) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_big,
            type: "bigint",
            maximum: check.value,
            inclusive: check.inclusive,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "multipleOf") {
        if (input.data % check.value !== BigInt(0)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.not_multiple_of,
            multipleOf: check.value,
            message: check.message
          });
          status.dirty();
        }
      } else {
        util.assertNever(check);
      }
    }
    return { status: status.value, value: input.data };
  }
  _getInvalidInput(input) {
    const ctx = this._getOrReturnCtx(input);
    addIssueToContext(ctx, {
      code: ZodIssueCode.invalid_type,
      expected: ZodParsedType.bigint,
      received: ctx.parsedType
    });
    return INVALID;
  }
  gte(value, message) {
    return this.setLimit("min", value, true, errorUtil.toString(message));
  }
  gt(value, message) {
    return this.setLimit("min", value, false, errorUtil.toString(message));
  }
  lte(value, message) {
    return this.setLimit("max", value, true, errorUtil.toString(message));
  }
  lt(value, message) {
    return this.setLimit("max", value, false, errorUtil.toString(message));
  }
  setLimit(kind, value, inclusive, message) {
    return new ZodBigInt({
      ...this._def,
      checks: [
        ...this._def.checks,
        {
          kind,
          value,
          inclusive,
          message: errorUtil.toString(message)
        }
      ]
    });
  }
  _addCheck(check) {
    return new ZodBigInt({
      ...this._def,
      checks: [...this._def.checks, check]
    });
  }
  positive(message) {
    return this._addCheck({
      kind: "min",
      value: BigInt(0),
      inclusive: false,
      message: errorUtil.toString(message)
    });
  }
  negative(message) {
    return this._addCheck({
      kind: "max",
      value: BigInt(0),
      inclusive: false,
      message: errorUtil.toString(message)
    });
  }
  nonpositive(message) {
    return this._addCheck({
      kind: "max",
      value: BigInt(0),
      inclusive: true,
      message: errorUtil.toString(message)
    });
  }
  nonnegative(message) {
    return this._addCheck({
      kind: "min",
      value: BigInt(0),
      inclusive: true,
      message: errorUtil.toString(message)
    });
  }
  multipleOf(value, message) {
    return this._addCheck({
      kind: "multipleOf",
      value,
      message: errorUtil.toString(message)
    });
  }
  get minValue() {
    let min = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "min") {
        if (min === null || ch.value > min)
          min = ch.value;
      }
    }
    return min;
  }
  get maxValue() {
    let max = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "max") {
        if (max === null || ch.value < max)
          max = ch.value;
      }
    }
    return max;
  }
}
ZodBigInt.create = (params) => {
  return new ZodBigInt({
    checks: [],
    typeName: ZodFirstPartyTypeKind.ZodBigInt,
    coerce: params?.coerce ?? false,
    ...processCreateParams(params)
  });
};

class ZodBoolean extends ZodType {
  _parse(input) {
    if (this._def.coerce) {
      input.data = Boolean(input.data);
    }
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.boolean) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.boolean,
        received: ctx.parsedType
      });
      return INVALID;
    }
    return OK(input.data);
  }
}
ZodBoolean.create = (params) => {
  return new ZodBoolean({
    typeName: ZodFirstPartyTypeKind.ZodBoolean,
    coerce: params?.coerce || false,
    ...processCreateParams(params)
  });
};

class ZodDate extends ZodType {
  _parse(input) {
    if (this._def.coerce) {
      input.data = new Date(input.data);
    }
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.date) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.date,
        received: ctx.parsedType
      });
      return INVALID;
    }
    if (Number.isNaN(input.data.getTime())) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_date
      });
      return INVALID;
    }
    const status = new ParseStatus;
    let ctx = undefined;
    for (const check of this._def.checks) {
      if (check.kind === "min") {
        if (input.data.getTime() < check.value) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_small,
            message: check.message,
            inclusive: true,
            exact: false,
            minimum: check.value,
            type: "date"
          });
          status.dirty();
        }
      } else if (check.kind === "max") {
        if (input.data.getTime() > check.value) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_big,
            message: check.message,
            inclusive: true,
            exact: false,
            maximum: check.value,
            type: "date"
          });
          status.dirty();
        }
      } else {
        util.assertNever(check);
      }
    }
    return {
      status: status.value,
      value: new Date(input.data.getTime())
    };
  }
  _addCheck(check) {
    return new ZodDate({
      ...this._def,
      checks: [...this._def.checks, check]
    });
  }
  min(minDate, message) {
    return this._addCheck({
      kind: "min",
      value: minDate.getTime(),
      message: errorUtil.toString(message)
    });
  }
  max(maxDate, message) {
    return this._addCheck({
      kind: "max",
      value: maxDate.getTime(),
      message: errorUtil.toString(message)
    });
  }
  get minDate() {
    let min = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "min") {
        if (min === null || ch.value > min)
          min = ch.value;
      }
    }
    return min != null ? new Date(min) : null;
  }
  get maxDate() {
    let max = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "max") {
        if (max === null || ch.value < max)
          max = ch.value;
      }
    }
    return max != null ? new Date(max) : null;
  }
}
ZodDate.create = (params) => {
  return new ZodDate({
    checks: [],
    coerce: params?.coerce || false,
    typeName: ZodFirstPartyTypeKind.ZodDate,
    ...processCreateParams(params)
  });
};

class ZodSymbol extends ZodType {
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.symbol) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.symbol,
        received: ctx.parsedType
      });
      return INVALID;
    }
    return OK(input.data);
  }
}
ZodSymbol.create = (params) => {
  return new ZodSymbol({
    typeName: ZodFirstPartyTypeKind.ZodSymbol,
    ...processCreateParams(params)
  });
};

class ZodUndefined extends ZodType {
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.undefined) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.undefined,
        received: ctx.parsedType
      });
      return INVALID;
    }
    return OK(input.data);
  }
}
ZodUndefined.create = (params) => {
  return new ZodUndefined({
    typeName: ZodFirstPartyTypeKind.ZodUndefined,
    ...processCreateParams(params)
  });
};

class ZodNull extends ZodType {
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.null) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.null,
        received: ctx.parsedType
      });
      return INVALID;
    }
    return OK(input.data);
  }
}
ZodNull.create = (params) => {
  return new ZodNull({
    typeName: ZodFirstPartyTypeKind.ZodNull,
    ...processCreateParams(params)
  });
};

class ZodAny extends ZodType {
  constructor() {
    super(...arguments);
    this._any = true;
  }
  _parse(input) {
    return OK(input.data);
  }
}
ZodAny.create = (params) => {
  return new ZodAny({
    typeName: ZodFirstPartyTypeKind.ZodAny,
    ...processCreateParams(params)
  });
};

class ZodUnknown extends ZodType {
  constructor() {
    super(...arguments);
    this._unknown = true;
  }
  _parse(input) {
    return OK(input.data);
  }
}
ZodUnknown.create = (params) => {
  return new ZodUnknown({
    typeName: ZodFirstPartyTypeKind.ZodUnknown,
    ...processCreateParams(params)
  });
};

class ZodNever extends ZodType {
  _parse(input) {
    const ctx = this._getOrReturnCtx(input);
    addIssueToContext(ctx, {
      code: ZodIssueCode.invalid_type,
      expected: ZodParsedType.never,
      received: ctx.parsedType
    });
    return INVALID;
  }
}
ZodNever.create = (params) => {
  return new ZodNever({
    typeName: ZodFirstPartyTypeKind.ZodNever,
    ...processCreateParams(params)
  });
};

class ZodVoid extends ZodType {
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.undefined) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.void,
        received: ctx.parsedType
      });
      return INVALID;
    }
    return OK(input.data);
  }
}
ZodVoid.create = (params) => {
  return new ZodVoid({
    typeName: ZodFirstPartyTypeKind.ZodVoid,
    ...processCreateParams(params)
  });
};

class ZodArray extends ZodType {
  _parse(input) {
    const { ctx, status } = this._processInputParams(input);
    const def = this._def;
    if (ctx.parsedType !== ZodParsedType.array) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.array,
        received: ctx.parsedType
      });
      return INVALID;
    }
    if (def.exactLength !== null) {
      const tooBig = ctx.data.length > def.exactLength.value;
      const tooSmall = ctx.data.length < def.exactLength.value;
      if (tooBig || tooSmall) {
        addIssueToContext(ctx, {
          code: tooBig ? ZodIssueCode.too_big : ZodIssueCode.too_small,
          minimum: tooSmall ? def.exactLength.value : undefined,
          maximum: tooBig ? def.exactLength.value : undefined,
          type: "array",
          inclusive: true,
          exact: true,
          message: def.exactLength.message
        });
        status.dirty();
      }
    }
    if (def.minLength !== null) {
      if (ctx.data.length < def.minLength.value) {
        addIssueToContext(ctx, {
          code: ZodIssueCode.too_small,
          minimum: def.minLength.value,
          type: "array",
          inclusive: true,
          exact: false,
          message: def.minLength.message
        });
        status.dirty();
      }
    }
    if (def.maxLength !== null) {
      if (ctx.data.length > def.maxLength.value) {
        addIssueToContext(ctx, {
          code: ZodIssueCode.too_big,
          maximum: def.maxLength.value,
          type: "array",
          inclusive: true,
          exact: false,
          message: def.maxLength.message
        });
        status.dirty();
      }
    }
    if (ctx.common.async) {
      return Promise.all([...ctx.data].map((item, i) => {
        return def.type._parseAsync(new ParseInputLazyPath(ctx, item, ctx.path, i));
      })).then((result) => {
        return ParseStatus.mergeArray(status, result);
      });
    }
    const result = [...ctx.data].map((item, i) => {
      return def.type._parseSync(new ParseInputLazyPath(ctx, item, ctx.path, i));
    });
    return ParseStatus.mergeArray(status, result);
  }
  get element() {
    return this._def.type;
  }
  min(minLength, message) {
    return new ZodArray({
      ...this._def,
      minLength: { value: minLength, message: errorUtil.toString(message) }
    });
  }
  max(maxLength, message) {
    return new ZodArray({
      ...this._def,
      maxLength: { value: maxLength, message: errorUtil.toString(message) }
    });
  }
  length(len, message) {
    return new ZodArray({
      ...this._def,
      exactLength: { value: len, message: errorUtil.toString(message) }
    });
  }
  nonempty(message) {
    return this.min(1, message);
  }
}
ZodArray.create = (schema, params) => {
  return new ZodArray({
    type: schema,
    minLength: null,
    maxLength: null,
    exactLength: null,
    typeName: ZodFirstPartyTypeKind.ZodArray,
    ...processCreateParams(params)
  });
};
function deepPartialify(schema) {
  if (schema instanceof ZodObject) {
    const newShape = {};
    for (const key in schema.shape) {
      const fieldSchema = schema.shape[key];
      newShape[key] = ZodOptional.create(deepPartialify(fieldSchema));
    }
    return new ZodObject({
      ...schema._def,
      shape: () => newShape
    });
  } else if (schema instanceof ZodArray) {
    return new ZodArray({
      ...schema._def,
      type: deepPartialify(schema.element)
    });
  } else if (schema instanceof ZodOptional) {
    return ZodOptional.create(deepPartialify(schema.unwrap()));
  } else if (schema instanceof ZodNullable) {
    return ZodNullable.create(deepPartialify(schema.unwrap()));
  } else if (schema instanceof ZodTuple) {
    return ZodTuple.create(schema.items.map((item) => deepPartialify(item)));
  } else {
    return schema;
  }
}

class ZodObject extends ZodType {
  constructor() {
    super(...arguments);
    this._cached = null;
    this.nonstrict = this.passthrough;
    this.augment = this.extend;
  }
  _getCached() {
    if (this._cached !== null)
      return this._cached;
    const shape = this._def.shape();
    const keys = util.objectKeys(shape);
    this._cached = { shape, keys };
    return this._cached;
  }
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.object) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.object,
        received: ctx.parsedType
      });
      return INVALID;
    }
    const { status, ctx } = this._processInputParams(input);
    const { shape, keys: shapeKeys } = this._getCached();
    const extraKeys = [];
    if (!(this._def.catchall instanceof ZodNever && this._def.unknownKeys === "strip")) {
      for (const key in ctx.data) {
        if (!shapeKeys.includes(key)) {
          extraKeys.push(key);
        }
      }
    }
    const pairs = [];
    for (const key of shapeKeys) {
      const keyValidator = shape[key];
      const value = ctx.data[key];
      pairs.push({
        key: { status: "valid", value: key },
        value: keyValidator._parse(new ParseInputLazyPath(ctx, value, ctx.path, key)),
        alwaysSet: key in ctx.data
      });
    }
    if (this._def.catchall instanceof ZodNever) {
      const unknownKeys = this._def.unknownKeys;
      if (unknownKeys === "passthrough") {
        for (const key of extraKeys) {
          pairs.push({
            key: { status: "valid", value: key },
            value: { status: "valid", value: ctx.data[key] }
          });
        }
      } else if (unknownKeys === "strict") {
        if (extraKeys.length > 0) {
          addIssueToContext(ctx, {
            code: ZodIssueCode.unrecognized_keys,
            keys: extraKeys
          });
          status.dirty();
        }
      } else if (unknownKeys === "strip") {} else {
        throw new Error(`Internal ZodObject error: invalid unknownKeys value.`);
      }
    } else {
      const catchall = this._def.catchall;
      for (const key of extraKeys) {
        const value = ctx.data[key];
        pairs.push({
          key: { status: "valid", value: key },
          value: catchall._parse(new ParseInputLazyPath(ctx, value, ctx.path, key)),
          alwaysSet: key in ctx.data
        });
      }
    }
    if (ctx.common.async) {
      return Promise.resolve().then(async () => {
        const syncPairs = [];
        for (const pair of pairs) {
          const key = await pair.key;
          const value = await pair.value;
          syncPairs.push({
            key,
            value,
            alwaysSet: pair.alwaysSet
          });
        }
        return syncPairs;
      }).then((syncPairs) => {
        return ParseStatus.mergeObjectSync(status, syncPairs);
      });
    } else {
      return ParseStatus.mergeObjectSync(status, pairs);
    }
  }
  get shape() {
    return this._def.shape();
  }
  strict(message) {
    errorUtil.errToObj;
    return new ZodObject({
      ...this._def,
      unknownKeys: "strict",
      ...message !== undefined ? {
        errorMap: (issue, ctx) => {
          const defaultError = this._def.errorMap?.(issue, ctx).message ?? ctx.defaultError;
          if (issue.code === "unrecognized_keys")
            return {
              message: errorUtil.errToObj(message).message ?? defaultError
            };
          return {
            message: defaultError
          };
        }
      } : {}
    });
  }
  strip() {
    return new ZodObject({
      ...this._def,
      unknownKeys: "strip"
    });
  }
  passthrough() {
    return new ZodObject({
      ...this._def,
      unknownKeys: "passthrough"
    });
  }
  extend(augmentation) {
    return new ZodObject({
      ...this._def,
      shape: () => ({
        ...this._def.shape(),
        ...augmentation
      })
    });
  }
  merge(merging) {
    const merged = new ZodObject({
      unknownKeys: merging._def.unknownKeys,
      catchall: merging._def.catchall,
      shape: () => ({
        ...this._def.shape(),
        ...merging._def.shape()
      }),
      typeName: ZodFirstPartyTypeKind.ZodObject
    });
    return merged;
  }
  setKey(key, schema) {
    return this.augment({ [key]: schema });
  }
  catchall(index) {
    return new ZodObject({
      ...this._def,
      catchall: index
    });
  }
  pick(mask) {
    const shape = {};
    for (const key of util.objectKeys(mask)) {
      if (mask[key] && this.shape[key]) {
        shape[key] = this.shape[key];
      }
    }
    return new ZodObject({
      ...this._def,
      shape: () => shape
    });
  }
  omit(mask) {
    const shape = {};
    for (const key of util.objectKeys(this.shape)) {
      if (!mask[key]) {
        shape[key] = this.shape[key];
      }
    }
    return new ZodObject({
      ...this._def,
      shape: () => shape
    });
  }
  deepPartial() {
    return deepPartialify(this);
  }
  partial(mask) {
    const newShape = {};
    for (const key of util.objectKeys(this.shape)) {
      const fieldSchema = this.shape[key];
      if (mask && !mask[key]) {
        newShape[key] = fieldSchema;
      } else {
        newShape[key] = fieldSchema.optional();
      }
    }
    return new ZodObject({
      ...this._def,
      shape: () => newShape
    });
  }
  required(mask) {
    const newShape = {};
    for (const key of util.objectKeys(this.shape)) {
      if (mask && !mask[key]) {
        newShape[key] = this.shape[key];
      } else {
        const fieldSchema = this.shape[key];
        let newField = fieldSchema;
        while (newField instanceof ZodOptional) {
          newField = newField._def.innerType;
        }
        newShape[key] = newField;
      }
    }
    return new ZodObject({
      ...this._def,
      shape: () => newShape
    });
  }
  keyof() {
    return createZodEnum(util.objectKeys(this.shape));
  }
}
ZodObject.create = (shape, params) => {
  return new ZodObject({
    shape: () => shape,
    unknownKeys: "strip",
    catchall: ZodNever.create(),
    typeName: ZodFirstPartyTypeKind.ZodObject,
    ...processCreateParams(params)
  });
};
ZodObject.strictCreate = (shape, params) => {
  return new ZodObject({
    shape: () => shape,
    unknownKeys: "strict",
    catchall: ZodNever.create(),
    typeName: ZodFirstPartyTypeKind.ZodObject,
    ...processCreateParams(params)
  });
};
ZodObject.lazycreate = (shape, params) => {
  return new ZodObject({
    shape,
    unknownKeys: "strip",
    catchall: ZodNever.create(),
    typeName: ZodFirstPartyTypeKind.ZodObject,
    ...processCreateParams(params)
  });
};

class ZodUnion extends ZodType {
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    const options = this._def.options;
    function handleResults(results) {
      for (const result of results) {
        if (result.result.status === "valid") {
          return result.result;
        }
      }
      for (const result of results) {
        if (result.result.status === "dirty") {
          ctx.common.issues.push(...result.ctx.common.issues);
          return result.result;
        }
      }
      const unionErrors = results.map((result) => new ZodError(result.ctx.common.issues));
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_union,
        unionErrors
      });
      return INVALID;
    }
    if (ctx.common.async) {
      return Promise.all(options.map(async (option) => {
        const childCtx = {
          ...ctx,
          common: {
            ...ctx.common,
            issues: []
          },
          parent: null
        };
        return {
          result: await option._parseAsync({
            data: ctx.data,
            path: ctx.path,
            parent: childCtx
          }),
          ctx: childCtx
        };
      })).then(handleResults);
    } else {
      let dirty = undefined;
      const issues = [];
      for (const option of options) {
        const childCtx = {
          ...ctx,
          common: {
            ...ctx.common,
            issues: []
          },
          parent: null
        };
        const result = option._parseSync({
          data: ctx.data,
          path: ctx.path,
          parent: childCtx
        });
        if (result.status === "valid") {
          return result;
        } else if (result.status === "dirty" && !dirty) {
          dirty = { result, ctx: childCtx };
        }
        if (childCtx.common.issues.length) {
          issues.push(childCtx.common.issues);
        }
      }
      if (dirty) {
        ctx.common.issues.push(...dirty.ctx.common.issues);
        return dirty.result;
      }
      const unionErrors = issues.map((issues) => new ZodError(issues));
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_union,
        unionErrors
      });
      return INVALID;
    }
  }
  get options() {
    return this._def.options;
  }
}
ZodUnion.create = (types, params) => {
  return new ZodUnion({
    options: types,
    typeName: ZodFirstPartyTypeKind.ZodUnion,
    ...processCreateParams(params)
  });
};
var getDiscriminator = (type) => {
  if (type instanceof ZodLazy) {
    return getDiscriminator(type.schema);
  } else if (type instanceof ZodEffects) {
    return getDiscriminator(type.innerType());
  } else if (type instanceof ZodLiteral) {
    return [type.value];
  } else if (type instanceof ZodEnum) {
    return type.options;
  } else if (type instanceof ZodNativeEnum) {
    return util.objectValues(type.enum);
  } else if (type instanceof ZodDefault) {
    return getDiscriminator(type._def.innerType);
  } else if (type instanceof ZodUndefined) {
    return [undefined];
  } else if (type instanceof ZodNull) {
    return [null];
  } else if (type instanceof ZodOptional) {
    return [undefined, ...getDiscriminator(type.unwrap())];
  } else if (type instanceof ZodNullable) {
    return [null, ...getDiscriminator(type.unwrap())];
  } else if (type instanceof ZodBranded) {
    return getDiscriminator(type.unwrap());
  } else if (type instanceof ZodReadonly) {
    return getDiscriminator(type.unwrap());
  } else if (type instanceof ZodCatch) {
    return getDiscriminator(type._def.innerType);
  } else {
    return [];
  }
};

class ZodDiscriminatedUnion extends ZodType {
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    if (ctx.parsedType !== ZodParsedType.object) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.object,
        received: ctx.parsedType
      });
      return INVALID;
    }
    const discriminator = this.discriminator;
    const discriminatorValue = ctx.data[discriminator];
    const option = this.optionsMap.get(discriminatorValue);
    if (!option) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_union_discriminator,
        options: Array.from(this.optionsMap.keys()),
        path: [discriminator]
      });
      return INVALID;
    }
    if (ctx.common.async) {
      return option._parseAsync({
        data: ctx.data,
        path: ctx.path,
        parent: ctx
      });
    } else {
      return option._parseSync({
        data: ctx.data,
        path: ctx.path,
        parent: ctx
      });
    }
  }
  get discriminator() {
    return this._def.discriminator;
  }
  get options() {
    return this._def.options;
  }
  get optionsMap() {
    return this._def.optionsMap;
  }
  static create(discriminator, options, params) {
    const optionsMap = new Map;
    for (const type of options) {
      const discriminatorValues = getDiscriminator(type.shape[discriminator]);
      if (!discriminatorValues.length) {
        throw new Error(`A discriminator value for key \`${discriminator}\` could not be extracted from all schema options`);
      }
      for (const value of discriminatorValues) {
        if (optionsMap.has(value)) {
          throw new Error(`Discriminator property ${String(discriminator)} has duplicate value ${String(value)}`);
        }
        optionsMap.set(value, type);
      }
    }
    return new ZodDiscriminatedUnion({
      typeName: ZodFirstPartyTypeKind.ZodDiscriminatedUnion,
      discriminator,
      options,
      optionsMap,
      ...processCreateParams(params)
    });
  }
}
function mergeValues(a, b) {
  const aType = getParsedType(a);
  const bType = getParsedType(b);
  if (a === b) {
    return { valid: true, data: a };
  } else if (aType === ZodParsedType.object && bType === ZodParsedType.object) {
    const bKeys = util.objectKeys(b);
    const sharedKeys = util.objectKeys(a).filter((key) => bKeys.indexOf(key) !== -1);
    const newObj = { ...a, ...b };
    for (const key of sharedKeys) {
      const sharedValue = mergeValues(a[key], b[key]);
      if (!sharedValue.valid) {
        return { valid: false };
      }
      newObj[key] = sharedValue.data;
    }
    return { valid: true, data: newObj };
  } else if (aType === ZodParsedType.array && bType === ZodParsedType.array) {
    if (a.length !== b.length) {
      return { valid: false };
    }
    const newArray = [];
    for (let index = 0;index < a.length; index++) {
      const itemA = a[index];
      const itemB = b[index];
      const sharedValue = mergeValues(itemA, itemB);
      if (!sharedValue.valid) {
        return { valid: false };
      }
      newArray.push(sharedValue.data);
    }
    return { valid: true, data: newArray };
  } else if (aType === ZodParsedType.date && bType === ZodParsedType.date && +a === +b) {
    return { valid: true, data: a };
  } else {
    return { valid: false };
  }
}

class ZodIntersection extends ZodType {
  _parse(input) {
    const { status, ctx } = this._processInputParams(input);
    const handleParsed = (parsedLeft, parsedRight) => {
      if (isAborted(parsedLeft) || isAborted(parsedRight)) {
        return INVALID;
      }
      const merged = mergeValues(parsedLeft.value, parsedRight.value);
      if (!merged.valid) {
        addIssueToContext(ctx, {
          code: ZodIssueCode.invalid_intersection_types
        });
        return INVALID;
      }
      if (isDirty(parsedLeft) || isDirty(parsedRight)) {
        status.dirty();
      }
      return { status: status.value, value: merged.data };
    };
    if (ctx.common.async) {
      return Promise.all([
        this._def.left._parseAsync({
          data: ctx.data,
          path: ctx.path,
          parent: ctx
        }),
        this._def.right._parseAsync({
          data: ctx.data,
          path: ctx.path,
          parent: ctx
        })
      ]).then(([left, right]) => handleParsed(left, right));
    } else {
      return handleParsed(this._def.left._parseSync({
        data: ctx.data,
        path: ctx.path,
        parent: ctx
      }), this._def.right._parseSync({
        data: ctx.data,
        path: ctx.path,
        parent: ctx
      }));
    }
  }
}
ZodIntersection.create = (left, right, params) => {
  return new ZodIntersection({
    left,
    right,
    typeName: ZodFirstPartyTypeKind.ZodIntersection,
    ...processCreateParams(params)
  });
};

class ZodTuple extends ZodType {
  _parse(input) {
    const { status, ctx } = this._processInputParams(input);
    if (ctx.parsedType !== ZodParsedType.array) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.array,
        received: ctx.parsedType
      });
      return INVALID;
    }
    if (ctx.data.length < this._def.items.length) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.too_small,
        minimum: this._def.items.length,
        inclusive: true,
        exact: false,
        type: "array"
      });
      return INVALID;
    }
    const rest = this._def.rest;
    if (!rest && ctx.data.length > this._def.items.length) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.too_big,
        maximum: this._def.items.length,
        inclusive: true,
        exact: false,
        type: "array"
      });
      status.dirty();
    }
    const items = [...ctx.data].map((item, itemIndex) => {
      const schema = this._def.items[itemIndex] || this._def.rest;
      if (!schema)
        return null;
      return schema._parse(new ParseInputLazyPath(ctx, item, ctx.path, itemIndex));
    }).filter((x) => !!x);
    if (ctx.common.async) {
      return Promise.all(items).then((results) => {
        return ParseStatus.mergeArray(status, results);
      });
    } else {
      return ParseStatus.mergeArray(status, items);
    }
  }
  get items() {
    return this._def.items;
  }
  rest(rest) {
    return new ZodTuple({
      ...this._def,
      rest
    });
  }
}
ZodTuple.create = (schemas, params) => {
  if (!Array.isArray(schemas)) {
    throw new Error("You must pass an array of schemas to z.tuple([ ... ])");
  }
  return new ZodTuple({
    items: schemas,
    typeName: ZodFirstPartyTypeKind.ZodTuple,
    rest: null,
    ...processCreateParams(params)
  });
};

class ZodRecord extends ZodType {
  get keySchema() {
    return this._def.keyType;
  }
  get valueSchema() {
    return this._def.valueType;
  }
  _parse(input) {
    const { status, ctx } = this._processInputParams(input);
    if (ctx.parsedType !== ZodParsedType.object) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.object,
        received: ctx.parsedType
      });
      return INVALID;
    }
    const pairs = [];
    const keyType = this._def.keyType;
    const valueType = this._def.valueType;
    for (const key in ctx.data) {
      pairs.push({
        key: keyType._parse(new ParseInputLazyPath(ctx, key, ctx.path, key)),
        value: valueType._parse(new ParseInputLazyPath(ctx, ctx.data[key], ctx.path, key)),
        alwaysSet: key in ctx.data
      });
    }
    if (ctx.common.async) {
      return ParseStatus.mergeObjectAsync(status, pairs);
    } else {
      return ParseStatus.mergeObjectSync(status, pairs);
    }
  }
  get element() {
    return this._def.valueType;
  }
  static create(first, second, third) {
    if (second instanceof ZodType) {
      return new ZodRecord({
        keyType: first,
        valueType: second,
        typeName: ZodFirstPartyTypeKind.ZodRecord,
        ...processCreateParams(third)
      });
    }
    return new ZodRecord({
      keyType: ZodString.create(),
      valueType: first,
      typeName: ZodFirstPartyTypeKind.ZodRecord,
      ...processCreateParams(second)
    });
  }
}

class ZodMap extends ZodType {
  get keySchema() {
    return this._def.keyType;
  }
  get valueSchema() {
    return this._def.valueType;
  }
  _parse(input) {
    const { status, ctx } = this._processInputParams(input);
    if (ctx.parsedType !== ZodParsedType.map) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.map,
        received: ctx.parsedType
      });
      return INVALID;
    }
    const keyType = this._def.keyType;
    const valueType = this._def.valueType;
    const pairs = [...ctx.data.entries()].map(([key, value], index) => {
      return {
        key: keyType._parse(new ParseInputLazyPath(ctx, key, ctx.path, [index, "key"])),
        value: valueType._parse(new ParseInputLazyPath(ctx, value, ctx.path, [index, "value"]))
      };
    });
    if (ctx.common.async) {
      const finalMap = new Map;
      return Promise.resolve().then(async () => {
        for (const pair of pairs) {
          const key = await pair.key;
          const value = await pair.value;
          if (key.status === "aborted" || value.status === "aborted") {
            return INVALID;
          }
          if (key.status === "dirty" || value.status === "dirty") {
            status.dirty();
          }
          finalMap.set(key.value, value.value);
        }
        return { status: status.value, value: finalMap };
      });
    } else {
      const finalMap = new Map;
      for (const pair of pairs) {
        const key = pair.key;
        const value = pair.value;
        if (key.status === "aborted" || value.status === "aborted") {
          return INVALID;
        }
        if (key.status === "dirty" || value.status === "dirty") {
          status.dirty();
        }
        finalMap.set(key.value, value.value);
      }
      return { status: status.value, value: finalMap };
    }
  }
}
ZodMap.create = (keyType, valueType, params) => {
  return new ZodMap({
    valueType,
    keyType,
    typeName: ZodFirstPartyTypeKind.ZodMap,
    ...processCreateParams(params)
  });
};

class ZodSet extends ZodType {
  _parse(input) {
    const { status, ctx } = this._processInputParams(input);
    if (ctx.parsedType !== ZodParsedType.set) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.set,
        received: ctx.parsedType
      });
      return INVALID;
    }
    const def = this._def;
    if (def.minSize !== null) {
      if (ctx.data.size < def.minSize.value) {
        addIssueToContext(ctx, {
          code: ZodIssueCode.too_small,
          minimum: def.minSize.value,
          type: "set",
          inclusive: true,
          exact: false,
          message: def.minSize.message
        });
        status.dirty();
      }
    }
    if (def.maxSize !== null) {
      if (ctx.data.size > def.maxSize.value) {
        addIssueToContext(ctx, {
          code: ZodIssueCode.too_big,
          maximum: def.maxSize.value,
          type: "set",
          inclusive: true,
          exact: false,
          message: def.maxSize.message
        });
        status.dirty();
      }
    }
    const valueType = this._def.valueType;
    function finalizeSet(elements) {
      const parsedSet = new Set;
      for (const element of elements) {
        if (element.status === "aborted")
          return INVALID;
        if (element.status === "dirty")
          status.dirty();
        parsedSet.add(element.value);
      }
      return { status: status.value, value: parsedSet };
    }
    const elements = [...ctx.data.values()].map((item, i) => valueType._parse(new ParseInputLazyPath(ctx, item, ctx.path, i)));
    if (ctx.common.async) {
      return Promise.all(elements).then((elements) => finalizeSet(elements));
    } else {
      return finalizeSet(elements);
    }
  }
  min(minSize, message) {
    return new ZodSet({
      ...this._def,
      minSize: { value: minSize, message: errorUtil.toString(message) }
    });
  }
  max(maxSize, message) {
    return new ZodSet({
      ...this._def,
      maxSize: { value: maxSize, message: errorUtil.toString(message) }
    });
  }
  size(size, message) {
    return this.min(size, message).max(size, message);
  }
  nonempty(message) {
    return this.min(1, message);
  }
}
ZodSet.create = (valueType, params) => {
  return new ZodSet({
    valueType,
    minSize: null,
    maxSize: null,
    typeName: ZodFirstPartyTypeKind.ZodSet,
    ...processCreateParams(params)
  });
};

class ZodFunction extends ZodType {
  constructor() {
    super(...arguments);
    this.validate = this.implement;
  }
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    if (ctx.parsedType !== ZodParsedType.function) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.function,
        received: ctx.parsedType
      });
      return INVALID;
    }
    function makeArgsIssue(args, error) {
      return makeIssue({
        data: args,
        path: ctx.path,
        errorMaps: [ctx.common.contextualErrorMap, ctx.schemaErrorMap, getErrorMap(), en_default].filter((x) => !!x),
        issueData: {
          code: ZodIssueCode.invalid_arguments,
          argumentsError: error
        }
      });
    }
    function makeReturnsIssue(returns, error) {
      return makeIssue({
        data: returns,
        path: ctx.path,
        errorMaps: [ctx.common.contextualErrorMap, ctx.schemaErrorMap, getErrorMap(), en_default].filter((x) => !!x),
        issueData: {
          code: ZodIssueCode.invalid_return_type,
          returnTypeError: error
        }
      });
    }
    const params = { errorMap: ctx.common.contextualErrorMap };
    const fn = ctx.data;
    if (this._def.returns instanceof ZodPromise) {
      const me = this;
      return OK(async function(...args) {
        const error = new ZodError([]);
        const parsedArgs = await me._def.args.parseAsync(args, params).catch((e) => {
          error.addIssue(makeArgsIssue(args, e));
          throw error;
        });
        const result = await Reflect.apply(fn, this, parsedArgs);
        const parsedReturns = await me._def.returns._def.type.parseAsync(result, params).catch((e) => {
          error.addIssue(makeReturnsIssue(result, e));
          throw error;
        });
        return parsedReturns;
      });
    } else {
      const me = this;
      return OK(function(...args) {
        const parsedArgs = me._def.args.safeParse(args, params);
        if (!parsedArgs.success) {
          throw new ZodError([makeArgsIssue(args, parsedArgs.error)]);
        }
        const result = Reflect.apply(fn, this, parsedArgs.data);
        const parsedReturns = me._def.returns.safeParse(result, params);
        if (!parsedReturns.success) {
          throw new ZodError([makeReturnsIssue(result, parsedReturns.error)]);
        }
        return parsedReturns.data;
      });
    }
  }
  parameters() {
    return this._def.args;
  }
  returnType() {
    return this._def.returns;
  }
  args(...items) {
    return new ZodFunction({
      ...this._def,
      args: ZodTuple.create(items).rest(ZodUnknown.create())
    });
  }
  returns(returnType) {
    return new ZodFunction({
      ...this._def,
      returns: returnType
    });
  }
  implement(func) {
    const validatedFunc = this.parse(func);
    return validatedFunc;
  }
  strictImplement(func) {
    const validatedFunc = this.parse(func);
    return validatedFunc;
  }
  static create(args, returns, params) {
    return new ZodFunction({
      args: args ? args : ZodTuple.create([]).rest(ZodUnknown.create()),
      returns: returns || ZodUnknown.create(),
      typeName: ZodFirstPartyTypeKind.ZodFunction,
      ...processCreateParams(params)
    });
  }
}

class ZodLazy extends ZodType {
  get schema() {
    return this._def.getter();
  }
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    const lazySchema = this._def.getter();
    return lazySchema._parse({ data: ctx.data, path: ctx.path, parent: ctx });
  }
}
ZodLazy.create = (getter, params) => {
  return new ZodLazy({
    getter,
    typeName: ZodFirstPartyTypeKind.ZodLazy,
    ...processCreateParams(params)
  });
};

class ZodLiteral extends ZodType {
  _parse(input) {
    if (input.data !== this._def.value) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        received: ctx.data,
        code: ZodIssueCode.invalid_literal,
        expected: this._def.value
      });
      return INVALID;
    }
    return { status: "valid", value: input.data };
  }
  get value() {
    return this._def.value;
  }
}
ZodLiteral.create = (value, params) => {
  return new ZodLiteral({
    value,
    typeName: ZodFirstPartyTypeKind.ZodLiteral,
    ...processCreateParams(params)
  });
};
function createZodEnum(values, params) {
  return new ZodEnum({
    values,
    typeName: ZodFirstPartyTypeKind.ZodEnum,
    ...processCreateParams(params)
  });
}

class ZodEnum extends ZodType {
  _parse(input) {
    if (typeof input.data !== "string") {
      const ctx = this._getOrReturnCtx(input);
      const expectedValues = this._def.values;
      addIssueToContext(ctx, {
        expected: util.joinValues(expectedValues),
        received: ctx.parsedType,
        code: ZodIssueCode.invalid_type
      });
      return INVALID;
    }
    if (!this._cache) {
      this._cache = new Set(this._def.values);
    }
    if (!this._cache.has(input.data)) {
      const ctx = this._getOrReturnCtx(input);
      const expectedValues = this._def.values;
      addIssueToContext(ctx, {
        received: ctx.data,
        code: ZodIssueCode.invalid_enum_value,
        options: expectedValues
      });
      return INVALID;
    }
    return OK(input.data);
  }
  get options() {
    return this._def.values;
  }
  get enum() {
    const enumValues = {};
    for (const val of this._def.values) {
      enumValues[val] = val;
    }
    return enumValues;
  }
  get Values() {
    const enumValues = {};
    for (const val of this._def.values) {
      enumValues[val] = val;
    }
    return enumValues;
  }
  get Enum() {
    const enumValues = {};
    for (const val of this._def.values) {
      enumValues[val] = val;
    }
    return enumValues;
  }
  extract(values, newDef = this._def) {
    return ZodEnum.create(values, {
      ...this._def,
      ...newDef
    });
  }
  exclude(values, newDef = this._def) {
    return ZodEnum.create(this.options.filter((opt) => !values.includes(opt)), {
      ...this._def,
      ...newDef
    });
  }
}
ZodEnum.create = createZodEnum;

class ZodNativeEnum extends ZodType {
  _parse(input) {
    const nativeEnumValues = util.getValidEnumValues(this._def.values);
    const ctx = this._getOrReturnCtx(input);
    if (ctx.parsedType !== ZodParsedType.string && ctx.parsedType !== ZodParsedType.number) {
      const expectedValues = util.objectValues(nativeEnumValues);
      addIssueToContext(ctx, {
        expected: util.joinValues(expectedValues),
        received: ctx.parsedType,
        code: ZodIssueCode.invalid_type
      });
      return INVALID;
    }
    if (!this._cache) {
      this._cache = new Set(util.getValidEnumValues(this._def.values));
    }
    if (!this._cache.has(input.data)) {
      const expectedValues = util.objectValues(nativeEnumValues);
      addIssueToContext(ctx, {
        received: ctx.data,
        code: ZodIssueCode.invalid_enum_value,
        options: expectedValues
      });
      return INVALID;
    }
    return OK(input.data);
  }
  get enum() {
    return this._def.values;
  }
}
ZodNativeEnum.create = (values, params) => {
  return new ZodNativeEnum({
    values,
    typeName: ZodFirstPartyTypeKind.ZodNativeEnum,
    ...processCreateParams(params)
  });
};

class ZodPromise extends ZodType {
  unwrap() {
    return this._def.type;
  }
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    if (ctx.parsedType !== ZodParsedType.promise && ctx.common.async === false) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.promise,
        received: ctx.parsedType
      });
      return INVALID;
    }
    const promisified = ctx.parsedType === ZodParsedType.promise ? ctx.data : Promise.resolve(ctx.data);
    return OK(promisified.then((data) => {
      return this._def.type.parseAsync(data, {
        path: ctx.path,
        errorMap: ctx.common.contextualErrorMap
      });
    }));
  }
}
ZodPromise.create = (schema, params) => {
  return new ZodPromise({
    type: schema,
    typeName: ZodFirstPartyTypeKind.ZodPromise,
    ...processCreateParams(params)
  });
};

class ZodEffects extends ZodType {
  innerType() {
    return this._def.schema;
  }
  sourceType() {
    return this._def.schema._def.typeName === ZodFirstPartyTypeKind.ZodEffects ? this._def.schema.sourceType() : this._def.schema;
  }
  _parse(input) {
    const { status, ctx } = this._processInputParams(input);
    const effect = this._def.effect || null;
    const checkCtx = {
      addIssue: (arg) => {
        addIssueToContext(ctx, arg);
        if (arg.fatal) {
          status.abort();
        } else {
          status.dirty();
        }
      },
      get path() {
        return ctx.path;
      }
    };
    checkCtx.addIssue = checkCtx.addIssue.bind(checkCtx);
    if (effect.type === "preprocess") {
      const processed = effect.transform(ctx.data, checkCtx);
      if (ctx.common.async) {
        return Promise.resolve(processed).then(async (processed) => {
          if (status.value === "aborted")
            return INVALID;
          const result = await this._def.schema._parseAsync({
            data: processed,
            path: ctx.path,
            parent: ctx
          });
          if (result.status === "aborted")
            return INVALID;
          if (result.status === "dirty")
            return DIRTY(result.value);
          if (status.value === "dirty")
            return DIRTY(result.value);
          return result;
        });
      } else {
        if (status.value === "aborted")
          return INVALID;
        const result = this._def.schema._parseSync({
          data: processed,
          path: ctx.path,
          parent: ctx
        });
        if (result.status === "aborted")
          return INVALID;
        if (result.status === "dirty")
          return DIRTY(result.value);
        if (status.value === "dirty")
          return DIRTY(result.value);
        return result;
      }
    }
    if (effect.type === "refinement") {
      const executeRefinement = (acc) => {
        const result = effect.refinement(acc, checkCtx);
        if (ctx.common.async) {
          return Promise.resolve(result);
        }
        if (result instanceof Promise) {
          throw new Error("Async refinement encountered during synchronous parse operation. Use .parseAsync instead.");
        }
        return acc;
      };
      if (ctx.common.async === false) {
        const inner = this._def.schema._parseSync({
          data: ctx.data,
          path: ctx.path,
          parent: ctx
        });
        if (inner.status === "aborted")
          return INVALID;
        if (inner.status === "dirty")
          status.dirty();
        executeRefinement(inner.value);
        return { status: status.value, value: inner.value };
      } else {
        return this._def.schema._parseAsync({ data: ctx.data, path: ctx.path, parent: ctx }).then((inner) => {
          if (inner.status === "aborted")
            return INVALID;
          if (inner.status === "dirty")
            status.dirty();
          return executeRefinement(inner.value).then(() => {
            return { status: status.value, value: inner.value };
          });
        });
      }
    }
    if (effect.type === "transform") {
      if (ctx.common.async === false) {
        const base = this._def.schema._parseSync({
          data: ctx.data,
          path: ctx.path,
          parent: ctx
        });
        if (!isValid(base))
          return INVALID;
        const result = effect.transform(base.value, checkCtx);
        if (result instanceof Promise) {
          throw new Error(`Asynchronous transform encountered during synchronous parse operation. Use .parseAsync instead.`);
        }
        return { status: status.value, value: result };
      } else {
        return this._def.schema._parseAsync({ data: ctx.data, path: ctx.path, parent: ctx }).then((base) => {
          if (!isValid(base))
            return INVALID;
          return Promise.resolve(effect.transform(base.value, checkCtx)).then((result) => ({
            status: status.value,
            value: result
          }));
        });
      }
    }
    util.assertNever(effect);
  }
}
ZodEffects.create = (schema, effect, params) => {
  return new ZodEffects({
    schema,
    typeName: ZodFirstPartyTypeKind.ZodEffects,
    effect,
    ...processCreateParams(params)
  });
};
ZodEffects.createWithPreprocess = (preprocess, schema, params) => {
  return new ZodEffects({
    schema,
    effect: { type: "preprocess", transform: preprocess },
    typeName: ZodFirstPartyTypeKind.ZodEffects,
    ...processCreateParams(params)
  });
};
class ZodOptional extends ZodType {
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType === ZodParsedType.undefined) {
      return OK(undefined);
    }
    return this._def.innerType._parse(input);
  }
  unwrap() {
    return this._def.innerType;
  }
}
ZodOptional.create = (type, params) => {
  return new ZodOptional({
    innerType: type,
    typeName: ZodFirstPartyTypeKind.ZodOptional,
    ...processCreateParams(params)
  });
};

class ZodNullable extends ZodType {
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType === ZodParsedType.null) {
      return OK(null);
    }
    return this._def.innerType._parse(input);
  }
  unwrap() {
    return this._def.innerType;
  }
}
ZodNullable.create = (type, params) => {
  return new ZodNullable({
    innerType: type,
    typeName: ZodFirstPartyTypeKind.ZodNullable,
    ...processCreateParams(params)
  });
};

class ZodDefault extends ZodType {
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    let data = ctx.data;
    if (ctx.parsedType === ZodParsedType.undefined) {
      data = this._def.defaultValue();
    }
    return this._def.innerType._parse({
      data,
      path: ctx.path,
      parent: ctx
    });
  }
  removeDefault() {
    return this._def.innerType;
  }
}
ZodDefault.create = (type, params) => {
  return new ZodDefault({
    innerType: type,
    typeName: ZodFirstPartyTypeKind.ZodDefault,
    defaultValue: typeof params.default === "function" ? params.default : () => params.default,
    ...processCreateParams(params)
  });
};

class ZodCatch extends ZodType {
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    const newCtx = {
      ...ctx,
      common: {
        ...ctx.common,
        issues: []
      }
    };
    const result = this._def.innerType._parse({
      data: newCtx.data,
      path: newCtx.path,
      parent: {
        ...newCtx
      }
    });
    if (isAsync(result)) {
      return result.then((result) => {
        return {
          status: "valid",
          value: result.status === "valid" ? result.value : this._def.catchValue({
            get error() {
              return new ZodError(newCtx.common.issues);
            },
            input: newCtx.data
          })
        };
      });
    } else {
      return {
        status: "valid",
        value: result.status === "valid" ? result.value : this._def.catchValue({
          get error() {
            return new ZodError(newCtx.common.issues);
          },
          input: newCtx.data
        })
      };
    }
  }
  removeCatch() {
    return this._def.innerType;
  }
}
ZodCatch.create = (type, params) => {
  return new ZodCatch({
    innerType: type,
    typeName: ZodFirstPartyTypeKind.ZodCatch,
    catchValue: typeof params.catch === "function" ? params.catch : () => params.catch,
    ...processCreateParams(params)
  });
};

class ZodNaN extends ZodType {
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.nan) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.nan,
        received: ctx.parsedType
      });
      return INVALID;
    }
    return { status: "valid", value: input.data };
  }
}
ZodNaN.create = (params) => {
  return new ZodNaN({
    typeName: ZodFirstPartyTypeKind.ZodNaN,
    ...processCreateParams(params)
  });
};
var BRAND = Symbol("zod_brand");

class ZodBranded extends ZodType {
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    const data = ctx.data;
    return this._def.type._parse({
      data,
      path: ctx.path,
      parent: ctx
    });
  }
  unwrap() {
    return this._def.type;
  }
}

class ZodPipeline extends ZodType {
  _parse(input) {
    const { status, ctx } = this._processInputParams(input);
    if (ctx.common.async) {
      const handleAsync = async () => {
        const inResult = await this._def.in._parseAsync({
          data: ctx.data,
          path: ctx.path,
          parent: ctx
        });
        if (inResult.status === "aborted")
          return INVALID;
        if (inResult.status === "dirty") {
          status.dirty();
          return DIRTY(inResult.value);
        } else {
          return this._def.out._parseAsync({
            data: inResult.value,
            path: ctx.path,
            parent: ctx
          });
        }
      };
      return handleAsync();
    } else {
      const inResult = this._def.in._parseSync({
        data: ctx.data,
        path: ctx.path,
        parent: ctx
      });
      if (inResult.status === "aborted")
        return INVALID;
      if (inResult.status === "dirty") {
        status.dirty();
        return {
          status: "dirty",
          value: inResult.value
        };
      } else {
        return this._def.out._parseSync({
          data: inResult.value,
          path: ctx.path,
          parent: ctx
        });
      }
    }
  }
  static create(a, b) {
    return new ZodPipeline({
      in: a,
      out: b,
      typeName: ZodFirstPartyTypeKind.ZodPipeline
    });
  }
}

class ZodReadonly extends ZodType {
  _parse(input) {
    const result = this._def.innerType._parse(input);
    const freeze = (data) => {
      if (isValid(data)) {
        data.value = Object.freeze(data.value);
      }
      return data;
    };
    return isAsync(result) ? result.then((data) => freeze(data)) : freeze(result);
  }
  unwrap() {
    return this._def.innerType;
  }
}
ZodReadonly.create = (type, params) => {
  return new ZodReadonly({
    innerType: type,
    typeName: ZodFirstPartyTypeKind.ZodReadonly,
    ...processCreateParams(params)
  });
};
function cleanParams(params, data) {
  const p = typeof params === "function" ? params(data) : typeof params === "string" ? { message: params } : params;
  const p2 = typeof p === "string" ? { message: p } : p;
  return p2;
}
function custom(check, _params = {}, fatal) {
  if (check)
    return ZodAny.create().superRefine((data, ctx) => {
      const r = check(data);
      if (r instanceof Promise) {
        return r.then((r) => {
          if (!r) {
            const params = cleanParams(_params, data);
            const _fatal = params.fatal ?? fatal ?? true;
            ctx.addIssue({ code: "custom", ...params, fatal: _fatal });
          }
        });
      }
      if (!r) {
        const params = cleanParams(_params, data);
        const _fatal = params.fatal ?? fatal ?? true;
        ctx.addIssue({ code: "custom", ...params, fatal: _fatal });
      }
      return;
    });
  return ZodAny.create();
}
var late = {
  object: ZodObject.lazycreate
};
var ZodFirstPartyTypeKind;
(function(ZodFirstPartyTypeKind) {
  ZodFirstPartyTypeKind["ZodString"] = "ZodString";
  ZodFirstPartyTypeKind["ZodNumber"] = "ZodNumber";
  ZodFirstPartyTypeKind["ZodNaN"] = "ZodNaN";
  ZodFirstPartyTypeKind["ZodBigInt"] = "ZodBigInt";
  ZodFirstPartyTypeKind["ZodBoolean"] = "ZodBoolean";
  ZodFirstPartyTypeKind["ZodDate"] = "ZodDate";
  ZodFirstPartyTypeKind["ZodSymbol"] = "ZodSymbol";
  ZodFirstPartyTypeKind["ZodUndefined"] = "ZodUndefined";
  ZodFirstPartyTypeKind["ZodNull"] = "ZodNull";
  ZodFirstPartyTypeKind["ZodAny"] = "ZodAny";
  ZodFirstPartyTypeKind["ZodUnknown"] = "ZodUnknown";
  ZodFirstPartyTypeKind["ZodNever"] = "ZodNever";
  ZodFirstPartyTypeKind["ZodVoid"] = "ZodVoid";
  ZodFirstPartyTypeKind["ZodArray"] = "ZodArray";
  ZodFirstPartyTypeKind["ZodObject"] = "ZodObject";
  ZodFirstPartyTypeKind["ZodUnion"] = "ZodUnion";
  ZodFirstPartyTypeKind["ZodDiscriminatedUnion"] = "ZodDiscriminatedUnion";
  ZodFirstPartyTypeKind["ZodIntersection"] = "ZodIntersection";
  ZodFirstPartyTypeKind["ZodTuple"] = "ZodTuple";
  ZodFirstPartyTypeKind["ZodRecord"] = "ZodRecord";
  ZodFirstPartyTypeKind["ZodMap"] = "ZodMap";
  ZodFirstPartyTypeKind["ZodSet"] = "ZodSet";
  ZodFirstPartyTypeKind["ZodFunction"] = "ZodFunction";
  ZodFirstPartyTypeKind["ZodLazy"] = "ZodLazy";
  ZodFirstPartyTypeKind["ZodLiteral"] = "ZodLiteral";
  ZodFirstPartyTypeKind["ZodEnum"] = "ZodEnum";
  ZodFirstPartyTypeKind["ZodEffects"] = "ZodEffects";
  ZodFirstPartyTypeKind["ZodNativeEnum"] = "ZodNativeEnum";
  ZodFirstPartyTypeKind["ZodOptional"] = "ZodOptional";
  ZodFirstPartyTypeKind["ZodNullable"] = "ZodNullable";
  ZodFirstPartyTypeKind["ZodDefault"] = "ZodDefault";
  ZodFirstPartyTypeKind["ZodCatch"] = "ZodCatch";
  ZodFirstPartyTypeKind["ZodPromise"] = "ZodPromise";
  ZodFirstPartyTypeKind["ZodBranded"] = "ZodBranded";
  ZodFirstPartyTypeKind["ZodPipeline"] = "ZodPipeline";
  ZodFirstPartyTypeKind["ZodReadonly"] = "ZodReadonly";
})(ZodFirstPartyTypeKind || (ZodFirstPartyTypeKind = {}));
var stringType = ZodString.create;
var numberType = ZodNumber.create;
var nanType = ZodNaN.create;
var bigIntType = ZodBigInt.create;
var booleanType = ZodBoolean.create;
var dateType = ZodDate.create;
var symbolType = ZodSymbol.create;
var undefinedType = ZodUndefined.create;
var nullType = ZodNull.create;
var anyType = ZodAny.create;
var unknownType = ZodUnknown.create;
var neverType = ZodNever.create;
var voidType = ZodVoid.create;
var arrayType = ZodArray.create;
var objectType = ZodObject.create;
var strictObjectType = ZodObject.strictCreate;
var unionType = ZodUnion.create;
var discriminatedUnionType = ZodDiscriminatedUnion.create;
var intersectionType = ZodIntersection.create;
var tupleType = ZodTuple.create;
var recordType = ZodRecord.create;
var mapType = ZodMap.create;
var setType = ZodSet.create;
var functionType = ZodFunction.create;
var lazyType = ZodLazy.create;
var literalType = ZodLiteral.create;
var enumType = ZodEnum.create;
var nativeEnumType = ZodNativeEnum.create;
var promiseType = ZodPromise.create;
var effectsType = ZodEffects.create;
var optionalType = ZodOptional.create;
var nullableType = ZodNullable.create;
var preprocessType = ZodEffects.createWithPreprocess;
var pipelineType = ZodPipeline.create;
// ../../../../tools/circuit-to-wokwi/node_modules/circuit-json/dist/index.mjs
var resistance = stringType().or(numberType()).transform((v) => parseAndConvertSiUnit(v, "Ω").value);
var capacitance = stringType().or(numberType()).transform((v) => parseAndConvertSiUnit(v, "F").value).transform((value) => {
  return Number.parseFloat(value.toPrecision(12));
});
var inductance = stringType().or(numberType()).transform((v) => parseAndConvertSiUnit(v, "H").value);
var voltage = stringType().or(numberType()).transform((v) => parseAndConvertSiUnit(v, "V").value);
var length = stringType().or(numberType()).transform((v) => parseAndConvertSiUnit(v).value);
var frequency = stringType().or(numberType()).transform((v) => parseAndConvertSiUnit(v, "Hz").value);
var distance = length;
var current = stringType().or(numberType()).transform((v) => parseAndConvertSiUnit(v, "A").value);
var duration_ms = stringType().or(numberType()).transform((v) => parseAndConvertSiUnit(v).value);
var time = duration_ms;
var ms = duration_ms;
var timestamp = stringType().datetime();
var rotation = stringType().or(numberType()).transform((arg) => {
  if (typeof arg === "number")
    return arg;
  if (arg.endsWith("deg")) {
    return Number.parseFloat(arg.split("deg")[0]);
  }
  if (arg.endsWith("rad")) {
    return Number.parseFloat(arg.split("rad")[0]) * 180 / Math.PI;
  }
  return Number.parseFloat(arg);
});
var battery_capacity = numberType().or(stringType().endsWith("mAh")).transform((v) => {
  if (typeof v === "string") {
    const valString = v.replace("mAh", "");
    const num = Number.parseFloat(valString);
    if (Number.isNaN(num)) {
      throw new Error("Invalid capacity");
    }
    return num;
  }
  return v;
}).describe("Battery capacity in mAh");
var expectTypesMatch = (shouldBe) => {};
expectTypesMatch("extra props b");
expectTypesMatch("missing props b");
expectTypesMatch(true);
expectTypesMatch("mismatched prop types: a");
var expectStringUnionsMatch = (shouldBe) => {};
expectStringUnionsMatch(true);
expectStringUnionsMatch('T1 has extra: "c", T2 has extra: "d"');
expectStringUnionsMatch('T1 has extra: "c"');
expectStringUnionsMatch('T2 has extra: "c"');
expectStringUnionsMatch('T1 has extra: "d", T2 has extra: "c"');
expectStringUnionsMatch(true);
var point = objectType({
  x: distance,
  y: distance
});
var position = point;
expectTypesMatch(true);
expectTypesMatch(true);
var point3 = objectType({
  x: distance,
  y: distance,
  z: distance
});
var position3 = point3;
expectTypesMatch(true);
var size = objectType({
  width: numberType(),
  height: numberType()
});
expectTypesMatch(true);
var randomId = (length4) => {
  const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  return Array.from({ length: length4 }, () => chars[Math.floor(Math.random() * chars.length)]).join("");
};
var getZodPrefixedIdWithDefault = (prefix) => {
  return stringType().optional().default(() => `${prefix}_${randomId(10)}`);
};
var ninePointAnchor = enumType([
  "top_left",
  "top_center",
  "top_right",
  "center_left",
  "center",
  "center_right",
  "bottom_left",
  "bottom_center",
  "bottom_right"
]);
expectTypesMatch(true);
var pcbRenderLayer = enumType([
  "top_silkscreen",
  "bottom_silkscreen",
  "top_copper",
  "bottom_copper",
  "top_soldermask",
  "bottom_soldermask",
  "top_fabrication_note",
  "bottom_fabrication_note",
  "top_user_note",
  "bottom_user_note",
  "top_courtyard",
  "bottom_courtyard",
  "inner1_copper",
  "inner2_copper",
  "inner3_copper",
  "inner4_copper",
  "inner5_copper",
  "inner6_copper",
  "inner7_copper",
  "inner8_copper",
  "edge_cuts",
  "drill"
]);
expectTypesMatch(true);
var asset = objectType({
  project_relative_path: stringType(),
  url: stringType(),
  mimetype: stringType()
});
expectTypesMatch(true);
var kicadAt = point.extend({
  rotation: rotation.optional()
});
expectTypesMatch(true);
var kicadFont = objectType({
  size: point.optional(),
  thickness: distance.optional()
});
expectTypesMatch(true);
var kicadEffects = objectType({
  font: kicadFont.optional()
});
expectTypesMatch(true);
var kicadProperty = objectType({
  value: stringType(),
  at: kicadAt.optional(),
  layer: stringType().optional(),
  uuid: stringType().optional(),
  hide: booleanType().optional(),
  effects: kicadEffects.optional()
});
expectTypesMatch(true);
var kicadFootprintProperties = objectType({
  Reference: kicadProperty.optional(),
  Value: kicadProperty.optional(),
  Datasheet: kicadProperty.optional(),
  Description: kicadProperty.optional()
});
expectTypesMatch(true);
var kicadFootprintAttributes = objectType({
  through_hole: booleanType().optional(),
  smd: booleanType().optional(),
  exclude_from_pos_files: booleanType().optional(),
  exclude_from_bom: booleanType().optional()
});
expectTypesMatch(true);
var kicadFootprintPad = objectType({
  name: stringType(),
  type: stringType(),
  shape: stringType().optional(),
  at: kicadAt.optional(),
  size: point.optional(),
  drill: distance.optional(),
  layers: arrayType(stringType()).optional(),
  removeUnusedLayers: booleanType().optional(),
  uuid: stringType().optional()
});
expectTypesMatch(true);
var kicadFootprintModel = objectType({
  path: stringType(),
  offset: point3.optional(),
  scale: point3.optional(),
  rotate: point3.optional()
});
expectTypesMatch(true);
var kicadFootprintMetadata = objectType({
  footprintName: stringType().optional(),
  version: unionType([numberType(), stringType()]).optional(),
  generator: stringType().optional(),
  generatorVersion: unionType([numberType(), stringType()]).optional(),
  layer: stringType().optional(),
  properties: kicadFootprintProperties.optional(),
  attributes: kicadFootprintAttributes.optional(),
  pads: arrayType(kicadFootprintPad).optional(),
  embeddedFonts: booleanType().optional(),
  model: kicadFootprintModel.optional()
});
expectTypesMatch(true);
var kicadSymbolPinNumbers = objectType({
  hide: booleanType().optional()
});
expectTypesMatch(true);
var kicadSymbolPinNames = objectType({
  offset: distance.optional(),
  hide: booleanType().optional()
});
expectTypesMatch(true);
var kicadSymbolEffects = objectType({
  font: kicadFont.optional(),
  justify: unionType([stringType(), arrayType(stringType())]).optional(),
  hide: booleanType().optional()
});
expectTypesMatch(true);
var kicadSymbolProperty = objectType({
  value: stringType(),
  id: unionType([numberType(), stringType()]).optional(),
  at: kicadAt.optional(),
  effects: kicadSymbolEffects.optional()
});
expectTypesMatch(true);
var kicadSymbolProperties = objectType({
  Reference: kicadSymbolProperty.optional(),
  Value: kicadSymbolProperty.optional(),
  Footprint: kicadSymbolProperty.optional(),
  Datasheet: kicadSymbolProperty.optional(),
  Description: kicadSymbolProperty.optional(),
  ki_keywords: kicadSymbolProperty.optional(),
  ki_fp_filters: kicadSymbolProperty.optional()
});
expectTypesMatch(true);
var kicadSymbolMetadata = objectType({
  symbolName: stringType().optional(),
  extends: stringType().optional(),
  pinNumbers: kicadSymbolPinNumbers.optional(),
  pinNames: kicadSymbolPinNames.optional(),
  excludeFromSim: booleanType().optional(),
  inBom: booleanType().optional(),
  onBoard: booleanType().optional(),
  properties: kicadSymbolProperties.optional(),
  embeddedFonts: booleanType().optional()
});
expectTypesMatch(true);
var base_circuit_json_error = objectType({
  error_type: stringType(),
  message: stringType(),
  is_fatal: booleanType().optional()
});
expectTypesMatch(true);
var supplier_name = enumType([
  "jlcpcb",
  "macrofab",
  "pcbway",
  "digikey",
  "mouser",
  "lcsc"
]);
expectTypesMatch(true);
var source_component_base = objectType({
  type: literalType("source_component"),
  ftype: stringType().optional(),
  source_component_id: stringType(),
  name: stringType(),
  manufacturer_part_number: stringType().optional(),
  supplier_part_numbers: recordType(supplier_name, arrayType(stringType())).optional(),
  display_value: stringType().optional(),
  display_name: stringType().optional(),
  are_pins_interchangeable: booleanType().optional(),
  internally_connected_source_port_ids: arrayType(arrayType(stringType())).optional(),
  source_group_id: stringType().optional(),
  subcircuit_id: stringType().optional()
});
expectTypesMatch(true);
var source_simple_capacitor = source_component_base.extend({
  ftype: literalType("simple_capacitor"),
  capacitance,
  max_voltage_rating: voltage.optional(),
  display_capacitance: stringType().optional(),
  max_decoupling_trace_length: distance.optional()
});
expectTypesMatch(true);
var source_simple_resistor = source_component_base.extend({
  ftype: literalType("simple_resistor"),
  resistance,
  display_resistance: stringType().optional()
});
expectTypesMatch(true);
var source_simple_diode = source_component_base.extend({
  ftype: literalType("simple_diode")
});
expectTypesMatch(true);
var source_simple_fiducial = source_component_base.extend({
  ftype: literalType("simple_fiducial")
});
expectTypesMatch(true);
var source_simple_led = source_simple_diode.extend({
  ftype: literalType("simple_led"),
  color: stringType().optional(),
  wavelength: stringType().optional()
});
expectTypesMatch(true);
var source_simple_ground = source_component_base.extend({
  ftype: literalType("simple_ground")
});
expectTypesMatch(true);
var source_simple_chip = source_component_base.extend({
  ftype: literalType("simple_chip")
});
expectTypesMatch(true);
var source_simple_power_source = source_component_base.extend({
  ftype: literalType("simple_power_source"),
  voltage
});
expectTypesMatch(true);
var source_simple_current_source = source_component_base.extend({
  ftype: literalType("simple_current_source"),
  current,
  frequency: frequency.optional(),
  peak_to_peak_current: current.optional(),
  wave_shape: enumType(["sine", "square", "triangle", "sawtooth", "dc"]).optional().default("dc"),
  phase: numberType().optional(),
  duty_cycle: numberType().min(0).max(1).optional()
});
expectTypesMatch(true);
var source_simple_fuse = source_component_base.extend({
  ftype: literalType("simple_fuse"),
  current_rating_amps: numberType().describe("Nominal current in amps the fuse is rated for"),
  voltage_rating_volts: numberType().describe("Voltage rating in volts, e.g. ±5V would be 5")
});
expectTypesMatch(true);
var source_simple_ammeter = source_component_base.extend({
  ftype: literalType("simple_ammeter")
});
expectTypesMatch(true);
var source_pin_attributes = objectType({
  must_be_connected: booleanType().optional(),
  provides_power: booleanType().optional(),
  requires_power: booleanType().optional(),
  provides_ground: booleanType().optional(),
  requires_ground: booleanType().optional(),
  provides_voltage: unionType([stringType(), numberType()]).optional(),
  requires_voltage: unionType([stringType(), numberType()]).optional(),
  do_not_connect: booleanType().optional(),
  include_in_board_pinout: booleanType().optional(),
  can_use_internal_pullup: booleanType().optional(),
  is_using_internal_pullup: booleanType().optional(),
  needs_external_pullup: booleanType().optional(),
  can_use_internal_pulldown: booleanType().optional(),
  is_using_internal_pulldown: booleanType().optional(),
  needs_external_pulldown: booleanType().optional(),
  can_use_open_drain: booleanType().optional(),
  is_using_open_drain: booleanType().optional(),
  can_use_push_pull: booleanType().optional(),
  is_using_push_pull: booleanType().optional(),
  should_have_decoupling_capacitor: booleanType().optional(),
  recommended_decoupling_capacitor_capacitance: unionType([stringType(), numberType()]).optional(),
  is_configured_for_i2c_sda: booleanType().optional(),
  is_configured_for_i2c_scl: booleanType().optional(),
  is_configured_for_spi_mosi: booleanType().optional(),
  is_configured_for_spi_miso: booleanType().optional(),
  is_configured_for_spi_sck: booleanType().optional(),
  is_configured_for_spi_cs: booleanType().optional(),
  is_configured_for_uart_tx: booleanType().optional(),
  is_configured_for_uart_rx: booleanType().optional(),
  supports_i2c_sda: booleanType().optional(),
  supports_i2c_scl: booleanType().optional(),
  supports_spi_mosi: booleanType().optional(),
  supports_spi_miso: booleanType().optional(),
  supports_spi_sck: booleanType().optional(),
  supports_spi_cs: booleanType().optional(),
  supports_uart_tx: booleanType().optional(),
  supports_uart_rx: booleanType().optional()
});
expectTypesMatch(true);
var source_simple_battery = source_component_base.extend({
  ftype: literalType("simple_battery"),
  capacity: battery_capacity
});
expectTypesMatch(true);
var source_simple_inductor = source_component_base.extend({
  ftype: literalType("simple_inductor"),
  inductance,
  display_inductance: stringType().optional(),
  max_current_rating: numberType().optional()
});
expectTypesMatch(true);
var source_simple_push_button = source_component_base.extend({
  ftype: literalType("simple_push_button")
});
expectTypesMatch(true);
var source_simple_potentiometer = source_component_base.extend({
  ftype: literalType("simple_potentiometer"),
  max_resistance: resistance,
  display_max_resistance: stringType().optional()
});
expectTypesMatch(true);
var source_simple_crystal = source_component_base.extend({
  ftype: literalType("simple_crystal"),
  frequency: numberType().describe("Frequency in Hz"),
  load_capacitance: numberType().optional().describe("Load capacitance in pF"),
  pin_variant: enumType(["two_pin", "four_pin"]).optional()
});
expectTypesMatch(true);
var source_simple_pin_header = source_component_base.extend({
  ftype: literalType("simple_pin_header"),
  pin_count: numberType(),
  gender: enumType(["male", "female"]).optional().default("male")
});
expectTypesMatch(true);
var source_simple_connector_standards = [
  "usb_c",
  "m2",
  "jst_sh",
  "jst_gh",
  "jst_zh",
  "jst_ph",
  "jst_xh",
  "jst_vh"
];
var source_simple_connector = source_component_base.extend({
  ftype: literalType("simple_connector"),
  standard: enumType(source_simple_connector_standards).optional(),
  pin_count: numberType().int().positive().optional()
});
expectTypesMatch(true);
var source_simple_pinout = source_component_base.extend({
  ftype: literalType("simple_pinout")
});
expectTypesMatch(true);
var source_simple_resonator = source_component_base.extend({
  ftype: literalType("simple_resonator"),
  load_capacitance: capacitance,
  equivalent_series_resistance: resistance.optional(),
  frequency
});
expectTypesMatch(true);
var source_simple_transistor = source_component_base.extend({
  ftype: literalType("simple_transistor"),
  transistor_type: enumType(["npn", "pnp"])
});
expectTypesMatch(true);
var source_simple_test_point = source_component_base.extend({
  ftype: literalType("simple_test_point"),
  footprint_variant: enumType(["pad", "through_hole"]).optional(),
  pad_shape: enumType(["rect", "circle"]).optional(),
  pad_diameter: unionType([numberType(), stringType()]).optional(),
  hole_diameter: unionType([numberType(), stringType()]).optional(),
  width: unionType([numberType(), stringType()]).optional(),
  height: unionType([numberType(), stringType()]).optional()
});
expectTypesMatch(true);
var source_simple_mosfet = source_component_base.extend({
  ftype: literalType("simple_mosfet"),
  channel_type: enumType(["n", "p"]),
  mosfet_mode: enumType(["enhancement", "depletion"])
});
expectTypesMatch(true);
var source_simple_op_amp = source_component_base.extend({
  ftype: literalType("simple_op_amp")
});
expectTypesMatch(true);
var source_simple_switch = source_component_base.extend({
  ftype: literalType("simple_switch")
});
expectTypesMatch(true);
var source_project_metadata = objectType({
  type: literalType("source_project_metadata"),
  name: stringType().optional(),
  software_used_string: stringType().optional(),
  project_url: stringType().optional(),
  source_filesystem_md5_hash: stringType().optional(),
  created_at: timestamp.optional()
});
expectTypesMatch(true);
var source_missing_property_error = base_circuit_json_error.extend({
  type: literalType("source_missing_property_error"),
  source_missing_property_error_id: getZodPrefixedIdWithDefault("source_missing_property_error"),
  source_component_id: stringType(),
  property_name: stringType(),
  subcircuit_id: stringType().optional(),
  error_type: literalType("source_missing_property_error").default("source_missing_property_error")
}).describe("The source code is missing a property");
expectTypesMatch(true);
var source_failed_to_create_component_error = base_circuit_json_error.extend({
  type: literalType("source_failed_to_create_component_error"),
  source_failed_to_create_component_error_id: getZodPrefixedIdWithDefault("source_failed_to_create_component_error"),
  error_type: literalType("source_failed_to_create_component_error").default("source_failed_to_create_component_error"),
  component_name: stringType().optional(),
  subcircuit_id: stringType().optional(),
  parent_source_component_id: stringType().optional(),
  pcb_center: objectType({
    x: numberType().optional(),
    y: numberType().optional()
  }).optional(),
  schematic_center: objectType({
    x: numberType().optional(),
    y: numberType().optional()
  }).optional()
}).describe("Error emitted when a component fails to be constructed");
expectTypesMatch(true);
var source_invalid_component_property_error = base_circuit_json_error.extend({
  type: literalType("source_invalid_component_property_error"),
  source_invalid_component_property_error_id: getZodPrefixedIdWithDefault("source_invalid_component_property_error"),
  source_component_id: stringType(),
  property_name: stringType(),
  property_value: unknownType().optional(),
  expected_format: stringType().optional(),
  subcircuit_id: stringType().optional(),
  error_type: literalType("source_invalid_component_property_error").default("source_invalid_component_property_error")
}).describe("The source component property is invalid");
expectTypesMatch(true);
var source_trace_not_connected_error = base_circuit_json_error.extend({
  type: literalType("source_trace_not_connected_error"),
  source_trace_not_connected_error_id: getZodPrefixedIdWithDefault("source_trace_not_connected_error"),
  error_type: literalType("source_trace_not_connected_error").default("source_trace_not_connected_error"),
  subcircuit_id: stringType().optional(),
  source_group_id: stringType().optional(),
  source_trace_id: stringType().optional(),
  connected_source_port_ids: arrayType(stringType()).optional(),
  selectors_not_found: arrayType(stringType()).optional()
}).describe("Occurs when a source trace selector does not match any ports");
expectTypesMatch(true);
var source_property_ignored_warning = objectType({
  type: literalType("source_property_ignored_warning"),
  source_property_ignored_warning_id: getZodPrefixedIdWithDefault("source_property_ignored_warning"),
  source_component_id: stringType(),
  property_name: stringType(),
  subcircuit_id: stringType().optional(),
  error_type: literalType("source_property_ignored_warning").default("source_property_ignored_warning"),
  message: stringType()
}).describe("The source property was ignored");
expectTypesMatch(true);
var source_pin_missing_trace_warning = objectType({
  type: literalType("source_pin_missing_trace_warning"),
  source_pin_missing_trace_warning_id: getZodPrefixedIdWithDefault("source_pin_missing_trace_warning"),
  warning_type: literalType("source_pin_missing_trace_warning").default("source_pin_missing_trace_warning"),
  message: stringType(),
  source_component_id: stringType(),
  source_port_id: stringType(),
  subcircuit_id: stringType().optional()
}).describe("Warning emitted when a source component pin is missing a trace connection");
expectTypesMatch(true);
var source_missing_manufacturer_part_number_warning = objectType({
  type: literalType("source_missing_manufacturer_part_number_warning"),
  source_missing_manufacturer_part_number_warning_id: getZodPrefixedIdWithDefault("source_missing_manufacturer_part_number_warning"),
  warning_type: literalType("source_missing_manufacturer_part_number_warning").default("source_missing_manufacturer_part_number_warning"),
  message: stringType(),
  source_component_id: stringType(),
  standard: stringType(),
  subcircuit_id: stringType().optional()
}).describe("Warning emitted when a standard connector is missing manufacturer part number");
expectTypesMatch(true);
var source_refdes_convention_warning = objectType({
  type: literalType("source_refdes_convention_warning"),
  source_refdes_convention_warning_id: getZodPrefixedIdWithDefault("source_refdes_convention_warning"),
  warning_type: literalType("source_refdes_convention_warning").default("source_refdes_convention_warning"),
  message: stringType(),
  source_component_id: stringType(),
  refdes: stringType(),
  source_component_ftype: stringType(),
  expected_prefixes: arrayType(stringType()),
  actual_prefix: stringType().optional(),
  subcircuit_id: stringType().optional()
}).describe("Warning emitted when a source component reference designator does not match the component type convention");
expectTypesMatch(true);
var source_simple_voltage_probe = source_component_base.extend({
  ftype: literalType("simple_voltage_probe")
});
expectTypesMatch(true);
var source_interconnect = source_component_base.extend({
  ftype: literalType("interconnect")
});
expectTypesMatch(true);
var source_i2c_misconfigured_error = base_circuit_json_error.extend({
  type: literalType("source_i2c_misconfigured_error"),
  source_i2c_misconfigured_error_id: getZodPrefixedIdWithDefault("source_i2c_misconfigured_error"),
  error_type: literalType("source_i2c_misconfigured_error").default("source_i2c_misconfigured_error"),
  source_port_ids: arrayType(stringType())
}).describe("Error emitted when incompatible I2C pins (e.g. SDA and SCL) are connected to the same net");
expectTypesMatch(true);
var source_component_misconfigured_error = base_circuit_json_error.extend({
  type: literalType("source_component_misconfigured_error"),
  source_component_misconfigured_error_id: getZodPrefixedIdWithDefault("source_component_misconfigured_error"),
  error_type: literalType("source_component_misconfigured_error").default("source_component_misconfigured_error"),
  source_component_ids: arrayType(stringType()),
  source_port_ids: arrayType(stringType()).optional()
}).describe("Error emitted when one or more source components have an invalid or conflicting configuration");
expectTypesMatch(true);
var source_simple_voltage_source = source_component_base.extend({
  ftype: literalType("simple_voltage_source"),
  voltage,
  frequency: frequency.optional(),
  peak_to_peak_voltage: voltage.optional(),
  wave_shape: enumType(["sinewave", "square", "triangle", "sawtooth"]).optional(),
  phase: rotation.optional(),
  duty_cycle: numberType().optional().describe("Duty cycle as a fraction (0 to 1)"),
  pulse_delay: ms.optional(),
  rise_time: ms.optional(),
  fall_time: ms.optional(),
  pulse_width: ms.optional(),
  period: ms.optional()
});
expectTypesMatch(true);
var any_source_component = unionType([
  source_simple_resistor,
  source_simple_capacitor,
  source_simple_diode,
  source_simple_fiducial,
  source_simple_led,
  source_simple_ground,
  source_simple_chip,
  source_simple_power_source,
  source_simple_current_source,
  source_simple_ammeter,
  source_simple_battery,
  source_simple_inductor,
  source_simple_push_button,
  source_simple_potentiometer,
  source_simple_crystal,
  source_simple_pin_header,
  source_simple_connector,
  source_simple_pinout,
  source_simple_resonator,
  source_simple_switch,
  source_simple_transistor,
  source_simple_test_point,
  source_simple_mosfet,
  source_simple_op_amp,
  source_simple_fuse,
  source_simple_voltage_probe,
  source_interconnect,
  source_simple_voltage_source,
  source_project_metadata,
  source_missing_property_error,
  source_invalid_component_property_error,
  source_failed_to_create_component_error,
  source_trace_not_connected_error,
  source_property_ignored_warning,
  source_pin_missing_trace_warning,
  source_missing_manufacturer_part_number_warning,
  source_refdes_convention_warning,
  source_i2c_misconfigured_error,
  source_component_misconfigured_error
]);
expectTypesMatch(true);
var source_port = objectType({
  type: literalType("source_port"),
  pin_number: numberType().optional(),
  port_hints: arrayType(stringType()).optional(),
  name: stringType(),
  source_port_id: stringType(),
  source_component_id: stringType().optional(),
  source_group_id: stringType().optional(),
  most_frequently_referenced_by_name: stringType().optional(),
  subcircuit_id: stringType().optional(),
  subcircuit_connectivity_map_key: stringType().optional()
}).merge(source_pin_attributes);
expectTypesMatch(true);
var source_component_internal_connection = objectType({
  type: literalType("source_component_internal_connection"),
  source_component_internal_connection_id: stringType(),
  source_component_id: stringType(),
  source_port_ids: arrayType(stringType()),
  subcircuit_id: stringType().optional()
});
expectTypesMatch(true);
var source_trace = objectType({
  type: literalType("source_trace"),
  source_trace_id: stringType(),
  connected_source_port_ids: arrayType(stringType()),
  connected_source_net_ids: arrayType(stringType()),
  subcircuit_id: stringType().optional(),
  subcircuit_connectivity_map_key: stringType().optional(),
  max_length: numberType().optional(),
  max_via_count: numberType().int().nonnegative().optional(),
  name: stringType().optional(),
  min_trace_thickness: numberType().optional(),
  display_name: stringType().optional()
});
expectTypesMatch(true);
var source_group = objectType({
  type: literalType("source_group"),
  source_group_id: stringType(),
  subcircuit_id: stringType().optional(),
  parent_subcircuit_id: stringType().optional(),
  parent_source_group_id: stringType().optional(),
  is_subcircuit: booleanType().optional(),
  show_as_schematic_box: booleanType().optional(),
  name: stringType().optional(),
  was_automatically_named: booleanType().optional()
});
expectTypesMatch(true);
var source_net = objectType({
  type: literalType("source_net"),
  source_net_id: stringType(),
  name: stringType(),
  member_source_group_ids: arrayType(stringType()),
  is_power: booleanType().optional(),
  is_ground: booleanType().optional(),
  is_digital_signal: booleanType().optional(),
  is_analog_signal: booleanType().optional(),
  is_positive_voltage_source: booleanType().optional(),
  trace_width: numberType().optional(),
  subcircuit_id: stringType().optional(),
  subcircuit_connectivity_map_key: stringType().optional()
});
expectTypesMatch(true);
var source_board = objectType({
  type: literalType("source_board"),
  source_board_id: stringType(),
  source_group_id: stringType(),
  title: stringType().optional()
}).describe("Defines a board in the source domain");
expectTypesMatch(true);
var source_ambiguous_port_reference = base_circuit_json_error.extend({
  type: literalType("source_ambiguous_port_reference"),
  source_ambiguous_port_reference_id: getZodPrefixedIdWithDefault("source_ambiguous_port_reference"),
  error_type: literalType("source_ambiguous_port_reference").default("source_ambiguous_port_reference"),
  source_port_id: stringType().optional(),
  source_component_id: stringType().optional()
}).describe("Error emitted when a port hint matches multiple non-overlapping pads, making the port reference ambiguous");
expectTypesMatch(true);
var source_pcb_ground_plane = objectType({
  type: literalType("source_pcb_ground_plane"),
  source_pcb_ground_plane_id: stringType(),
  source_group_id: stringType(),
  source_net_id: stringType(),
  subcircuit_id: stringType().optional()
}).describe("Defines a ground plane in the source domain");
expectTypesMatch(true);
var all_layers = [
  "top",
  "bottom",
  "inner1",
  "inner2",
  "inner3",
  "inner4",
  "inner5",
  "inner6",
  "inner7",
  "inner8"
];
var layer_string = enumType(all_layers);
var layer_ref = layer_string.or(objectType({
  name: layer_string
})).transform((layer) => {
  if (typeof layer === "string") {
    return layer;
  }
  return layer.name;
});
expectTypesMatch(true);
var visible_layer = enumType(["top", "bottom"]);
var source_manually_placed_via = objectType({
  type: literalType("source_manually_placed_via"),
  source_manually_placed_via_id: stringType(),
  source_group_id: stringType(),
  source_net_id: stringType().min(1).optional(),
  subcircuit_id: stringType().optional(),
  source_trace_id: stringType().optional()
}).describe("Defines a via that is manually placed in the source domain");
expectTypesMatch(true);
var source_unnamed_trace_warning = objectType({
  type: literalType("source_unnamed_trace_warning"),
  source_unnamed_trace_warning_id: getZodPrefixedIdWithDefault("source_unnamed_trace_warning"),
  warning_type: literalType("source_unnamed_trace_warning").default("source_unnamed_trace_warning"),
  message: stringType(),
  source_trace_id: stringType(),
  subcircuit_id: stringType().optional()
}).describe("Warning emitted when a source trace is missing a name");
expectTypesMatch(true);
var source_no_power_pin_defined_warning = objectType({
  type: literalType("source_no_power_pin_defined_warning"),
  source_no_power_pin_defined_warning_id: getZodPrefixedIdWithDefault("source_no_power_pin_defined_warning"),
  warning_type: literalType("source_no_power_pin_defined_warning").default("source_no_power_pin_defined_warning"),
  message: stringType(),
  source_component_id: stringType(),
  source_port_ids: arrayType(stringType()),
  subcircuit_id: stringType().optional()
}).describe("Warning emitted when a chip has no source ports with requires_power=true");
expectTypesMatch(true);
var source_no_ground_pin_defined_warning = objectType({
  type: literalType("source_no_ground_pin_defined_warning"),
  source_no_ground_pin_defined_warning_id: getZodPrefixedIdWithDefault("source_no_ground_pin_defined_warning"),
  warning_type: literalType("source_no_ground_pin_defined_warning").default("source_no_ground_pin_defined_warning"),
  message: stringType(),
  source_component_id: stringType(),
  source_port_ids: arrayType(stringType()),
  subcircuit_id: stringType().optional()
}).describe("Warning emitted when a chip has no source ports marked as ground pins");
expectTypesMatch(true);
var source_component_pins_underspecified_warning = objectType({
  type: literalType("source_component_pins_underspecified_warning"),
  source_component_pins_underspecified_warning_id: getZodPrefixedIdWithDefault("source_component_pins_underspecified_warning"),
  warning_type: literalType("source_component_pins_underspecified_warning").default("source_component_pins_underspecified_warning"),
  message: stringType(),
  source_component_id: stringType(),
  source_port_ids: arrayType(stringType()),
  subcircuit_id: stringType().optional()
}).describe("Warning emitted when all ports on a source component are underspecified");
expectTypesMatch(true);
var source_pin_must_be_connected_error = base_circuit_json_error.extend({
  type: literalType("source_pin_must_be_connected_error"),
  source_pin_must_be_connected_error_id: getZodPrefixedIdWithDefault("source_pin_must_be_connected_error"),
  error_type: literalType("source_pin_must_be_connected_error").default("source_pin_must_be_connected_error"),
  source_component_id: stringType(),
  source_port_id: stringType(),
  subcircuit_id: stringType().optional()
}).describe("Error emitted when a pin with mustBeConnected attribute is not connected to any trace");
expectTypesMatch(true);
var unknown_error_finding_part = base_circuit_json_error.extend({
  type: literalType("unknown_error_finding_part"),
  unknown_error_finding_part_id: getZodPrefixedIdWithDefault("unknown_error_finding_part"),
  error_type: literalType("unknown_error_finding_part").default("unknown_error_finding_part"),
  source_component_id: stringType().optional(),
  subcircuit_id: stringType().optional()
}).describe("Error emitted when an unexpected error occurs while finding a part");
expectTypesMatch(true);
var source_part_not_found_warning = objectType({
  type: literalType("source_part_not_found_warning"),
  source_part_not_found_warning_id: getZodPrefixedIdWithDefault("source_part_not_found_warning"),
  warning_type: literalType("source_part_not_found_warning").default("source_part_not_found_warning"),
  message: stringType(),
  source_component_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  supplier_name: supplier_name.optional(),
  manufacturer_part_number: stringType().optional(),
  supplier_part_number: stringType().optional(),
  part_name: stringType().optional()
}).describe("Warning emitted when a requested part can not be found");
expectTypesMatch(true);
var source_confusing_net_name_warning = objectType({
  type: literalType("source_confusing_net_name_warning"),
  source_confusing_net_name_warning_id: getZodPrefixedIdWithDefault("source_confusing_net_name_warning"),
  warning_type: literalType("source_confusing_net_name_warning").default("source_confusing_net_name_warning"),
  message: stringType(),
  source_net_ids: arrayType(stringType()).min(2),
  net_name: stringType(),
  subcircuit_id: stringType().optional()
}).describe("Warning emitted when electrically disconnected source nets share a name");
expectTypesMatch(true);
var source_bus = objectType({
  type: literalType("source_bus"),
  source_bus_id: stringType(),
  name: stringType().optional(),
  source_trace_ids: arrayType(stringType()).min(1),
  max_length_skew: numberType().nonnegative().finite().optional(),
  subcircuit_id: stringType().optional()
});
expectTypesMatch(true);
var schematic_box = objectType({
  type: literalType("schematic_box"),
  schematic_sheet_id: stringType().optional(),
  schematic_component_id: stringType().optional(),
  schematic_symbol_id: stringType().optional(),
  width: distance,
  height: distance,
  is_dashed: booleanType().default(false),
  x: distance,
  y: distance,
  subcircuit_id: stringType().optional()
}).describe("Draws a box on the schematic");
expectTypesMatch(true);
var schematic_path = objectType({
  type: literalType("schematic_path"),
  schematic_path_id: getZodPrefixedIdWithDefault("schematic_path"),
  schematic_sheet_id: stringType().optional(),
  schematic_component_id: stringType().optional(),
  schematic_symbol_id: stringType().optional(),
  fill_color: stringType().optional(),
  is_filled: booleanType().optional(),
  is_dashed: booleanType().default(false),
  stroke_width: distance.nullable().optional(),
  stroke_color: stringType().optional(),
  dash_length: distance.optional(),
  dash_gap: distance.optional(),
  points: arrayType(point),
  subcircuit_id: stringType().optional()
});
expectTypesMatch(true);
var schematic_pin_styles = recordType(objectType({
  left_margin: length.optional(),
  right_margin: length.optional(),
  top_margin: length.optional(),
  bottom_margin: length.optional()
}));
var schematic_component_port_arrangement_by_size = objectType({
  left_size: numberType(),
  right_size: numberType(),
  top_size: numberType().optional(),
  bottom_size: numberType().optional()
});
expectTypesMatch(true);
var schematic_component_port_arrangement_by_sides = objectType({
  left_side: objectType({
    pins: arrayType(numberType()),
    direction: enumType(["top-to-bottom", "bottom-to-top"]).optional()
  }).optional(),
  right_side: objectType({
    pins: arrayType(numberType()),
    direction: enumType(["top-to-bottom", "bottom-to-top"]).optional()
  }).optional(),
  top_side: objectType({
    pins: arrayType(numberType()),
    direction: enumType(["left-to-right", "right-to-left"]).optional()
  }).optional(),
  bottom_side: objectType({
    pins: arrayType(numberType()),
    direction: enumType(["left-to-right", "right-to-left"]).optional()
  }).optional()
});
expectTypesMatch(true);
var port_arrangement = unionType([
  schematic_component_port_arrangement_by_size,
  schematic_component_port_arrangement_by_sides
]);
var schematic_component = objectType({
  type: literalType("schematic_component"),
  size,
  center: point,
  source_component_id: stringType().optional(),
  schematic_component_id: stringType(),
  schematic_sheet_id: stringType().optional(),
  schematic_symbol_id: stringType().optional(),
  pin_spacing: length.optional(),
  pin_styles: schematic_pin_styles.optional(),
  box_width: length.optional(),
  symbol_name: stringType().optional(),
  port_arrangement: port_arrangement.optional(),
  port_labels: recordType(stringType()).optional(),
  symbol_display_value: stringType().optional(),
  subcircuit_id: stringType().optional(),
  schematic_group_id: stringType().optional(),
  is_schematic_group: booleanType().optional(),
  source_group_id: stringType().optional(),
  is_box_with_pins: booleanType().optional().default(true)
});
expectTypesMatch(true);
var schematicSymbolMetadata = objectType({
  kicad_symbol: kicadSymbolMetadata.optional()
}).catchall(unknownType());
var schematic_symbol = objectType({
  type: literalType("schematic_symbol"),
  schematic_symbol_id: stringType(),
  name: stringType().optional(),
  metadata: schematicSymbolMetadata.optional()
}).describe("Defines a named schematic symbol that can be referenced by components.");
expectTypesMatch(true);
var schematic_line = objectType({
  type: literalType("schematic_line"),
  schematic_line_id: getZodPrefixedIdWithDefault("schematic_line"),
  schematic_sheet_id: stringType().optional(),
  schematic_component_id: stringType().optional(),
  schematic_symbol_id: stringType().optional(),
  x1: distance,
  y1: distance,
  x2: distance,
  y2: distance,
  stroke_width: distance.nullable().optional(),
  color: stringType().default("#000000"),
  is_dashed: booleanType().default(false),
  dash_length: distance.optional(),
  dash_gap: distance.optional(),
  subcircuit_id: stringType().optional()
}).describe("Draws a styled line on the schematic");
expectTypesMatch(true);
var schematic_rect = objectType({
  type: literalType("schematic_rect"),
  schematic_rect_id: getZodPrefixedIdWithDefault("schematic_rect"),
  schematic_sheet_id: stringType().optional(),
  schematic_component_id: stringType().optional(),
  schematic_symbol_id: stringType().optional(),
  center: point,
  width: distance,
  height: distance,
  rotation: rotation.default(0),
  stroke_width: distance.nullable().optional(),
  color: stringType().default("#000000"),
  is_filled: booleanType().default(false),
  fill_color: stringType().optional(),
  is_dashed: booleanType().default(false),
  subcircuit_id: stringType().optional()
}).describe("Draws a styled rectangle on the schematic");
expectTypesMatch(true);
var schematic_circle = objectType({
  type: literalType("schematic_circle"),
  schematic_circle_id: getZodPrefixedIdWithDefault("schematic_circle"),
  schematic_sheet_id: stringType().optional(),
  schematic_component_id: stringType().optional(),
  schematic_symbol_id: stringType().optional(),
  center: point,
  radius: distance,
  stroke_width: distance.nullable().optional(),
  color: stringType().default("#000000"),
  is_filled: booleanType().default(false),
  fill_color: stringType().optional(),
  is_dashed: booleanType().default(false),
  subcircuit_id: stringType().optional()
}).describe("Draws a styled circle on the schematic");
expectTypesMatch(true);
var schematic_arc = objectType({
  type: literalType("schematic_arc"),
  schematic_arc_id: getZodPrefixedIdWithDefault("schematic_arc"),
  schematic_sheet_id: stringType().optional(),
  schematic_component_id: stringType().optional(),
  schematic_symbol_id: stringType().optional(),
  center: point,
  radius: distance,
  start_angle_degrees: rotation,
  end_angle_degrees: rotation,
  direction: enumType(["clockwise", "counterclockwise"]).default("counterclockwise"),
  stroke_width: distance.nullable().optional(),
  color: stringType().default("#000000"),
  is_dashed: booleanType().default(false),
  subcircuit_id: stringType().optional()
}).describe("Draws a styled arc on the schematic");
expectTypesMatch(true);
var schematic_trace = objectType({
  type: literalType("schematic_trace"),
  schematic_trace_id: stringType(),
  schematic_sheet_id: stringType().optional(),
  source_trace_id: stringType().optional(),
  junctions: arrayType(objectType({
    x: numberType(),
    y: numberType()
  })),
  edges: arrayType(objectType({
    from: objectType({
      x: numberType(),
      y: numberType()
    }),
    to: objectType({
      x: numberType(),
      y: numberType()
    }),
    is_crossing: booleanType().optional(),
    from_schematic_port_id: stringType().optional(),
    to_schematic_port_id: stringType().optional()
  })),
  subcircuit_id: stringType().optional(),
  subcircuit_connectivity_map_key: stringType().optional()
});
expectTypesMatch(true);
var fivePointAnchor = enumType([
  "center",
  "left",
  "right",
  "top",
  "bottom"
]);
expectTypesMatch(true);
var schematic_text_part = objectType({
  text: stringType(),
  is_overlined: booleanType().optional()
});
var schematic_text = objectType({
  type: literalType("schematic_text"),
  schematic_sheet_id: stringType().optional(),
  schematic_component_id: stringType().optional(),
  schematic_symbol_id: stringType().optional(),
  schematic_text_id: stringType(),
  source_trace_id: stringType().optional(),
  text: stringType(),
  text_parts: arrayType(schematic_text_part).min(1).optional(),
  display_superscript: stringType().optional(),
  font_size: numberType().default(0.18),
  position: objectType({
    x: distance,
    y: distance
  }),
  rotation: numberType().default(0),
  anchor: unionType([fivePointAnchor.describe("legacy"), ninePointAnchor]).default("center"),
  color: stringType().default("#000000"),
  subcircuit_id: stringType().optional()
});
expectTypesMatch(true);
var schematic_port = objectType({
  type: literalType("schematic_port"),
  schematic_port_id: stringType(),
  source_port_id: stringType(),
  schematic_sheet_id: stringType().optional(),
  schematic_component_id: stringType().optional(),
  center: point,
  facing_direction: enumType(["up", "down", "left", "right"]).optional(),
  distance_from_component_edge: numberType().optional(),
  side_of_component: enumType(["top", "bottom", "left", "right"]).optional(),
  true_ccw_index: numberType().optional(),
  pin_number: numberType().optional(),
  display_pin_label: stringType().optional(),
  display_pin_label_text_parts: arrayType(schematic_text_part).min(1).optional(),
  display_pin_label_font_size: numberType().positive().finite().optional(),
  subcircuit_id: stringType().optional(),
  is_connected: booleanType().optional(),
  is_internal_circuit_port: booleanType().optional(),
  is_overlapping_internal_circuit_port: booleanType().optional(),
  has_input_arrow: booleanType().optional(),
  has_output_arrow: booleanType().optional(),
  is_drawn_with_inversion_circle: booleanType().optional()
}).describe("Defines a port on a schematic component");
expectTypesMatch(true);
var schematic_net_label = objectType({
  type: literalType("schematic_net_label"),
  schematic_net_label_id: getZodPrefixedIdWithDefault("schematic_net_label"),
  schematic_sheet_id: stringType().optional(),
  schematic_trace_id: stringType().optional(),
  source_trace_id: stringType().optional(),
  source_net_id: stringType(),
  center: point,
  anchor_position: point.optional(),
  anchor_side: enumType(["top", "bottom", "left", "right"]),
  text: stringType(),
  display_superscript: stringType().optional(),
  symbol_name: stringType().optional(),
  is_movable: booleanType().optional(),
  subcircuit_id: stringType().optional()
});
expectTypesMatch(true);
var schematic_error = base_circuit_json_error.extend({
  type: literalType("schematic_error"),
  schematic_error_id: stringType(),
  error_type: literalType("schematic_port_not_found").default("schematic_port_not_found"),
  subcircuit_id: stringType().optional()
}).describe("Defines a schematic error on the schematic");
expectTypesMatch(true);
var schematic_layout_error = base_circuit_json_error.extend({
  type: literalType("schematic_layout_error"),
  schematic_layout_error_id: getZodPrefixedIdWithDefault("schematic_layout_error"),
  error_type: literalType("schematic_layout_error").default("schematic_layout_error"),
  source_group_id: stringType(),
  schematic_group_id: stringType(),
  subcircuit_id: stringType().optional()
}).describe("Error emitted when schematic layout fails for a group");
expectTypesMatch(true);
var schematic_debug_object_base = objectType({
  type: literalType("schematic_debug_object"),
  label: stringType().optional(),
  subcircuit_id: stringType().optional()
});
var schematic_debug_rect = schematic_debug_object_base.extend({
  shape: literalType("rect"),
  center: point,
  size
});
var schematic_debug_line = schematic_debug_object_base.extend({
  shape: literalType("line"),
  start: point,
  end: point
});
var schematic_debug_point = schematic_debug_object_base.extend({
  shape: literalType("point"),
  center: point
});
var schematic_debug_object = discriminatedUnionType("shape", [
  schematic_debug_rect,
  schematic_debug_line,
  schematic_debug_point
]);
expectTypesMatch(true);
var schematic_voltage_probe = objectType({
  type: literalType("schematic_voltage_probe"),
  schematic_voltage_probe_id: stringType(),
  schematic_sheet_id: stringType().optional(),
  source_component_id: stringType().optional(),
  name: stringType().optional(),
  position: point,
  schematic_trace_id: stringType(),
  voltage: voltage.optional(),
  subcircuit_id: stringType().optional(),
  color: stringType().optional(),
  label_alignment: ninePointAnchor.optional()
}).describe("Defines a voltage probe measurement point on a schematic trace");
expectTypesMatch(true);
var schematic_manual_edit_conflict_warning = objectType({
  type: literalType("schematic_manual_edit_conflict_warning"),
  schematic_manual_edit_conflict_warning_id: getZodPrefixedIdWithDefault("schematic_manual_edit_conflict_warning"),
  warning_type: literalType("schematic_manual_edit_conflict_warning").default("schematic_manual_edit_conflict_warning"),
  message: stringType(),
  schematic_component_id: stringType(),
  schematic_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  source_component_id: stringType()
}).describe("Warning emitted when a component has both manual placement and explicit schX/schY coordinates");
expectTypesMatch(true);
var schematic_component_overlap_warning = objectType({
  type: literalType("schematic_component_overlap_warning"),
  schematic_component_overlap_warning_id: getZodPrefixedIdWithDefault("schematic_component_overlap_warning"),
  warning_type: literalType("schematic_component_overlap_warning").default("schematic_component_overlap_warning"),
  message: stringType(),
  schematic_component_ids: tupleType([stringType(), stringType()]),
  schematic_sheet_id: stringType().optional()
}).describe("Warning emitted when the rendered bounds of two schematic components overlap");
expectTypesMatch(true);
var schematic_component_styling_warning = objectType({
  type: literalType("schematic_component_styling_warning"),
  schematic_component_styling_warning_id: getZodPrefixedIdWithDefault("schematic_component_styling_warning"),
  warning_type: literalType("schematic_component_styling_warning").default("schematic_component_styling_warning"),
  message: stringType(),
  schematic_component_id: stringType(),
  styling_issue_type: stringType(),
  schematic_port_ids: arrayType(stringType()).optional(),
  source_component_id: stringType().optional(),
  schematic_sheet_id: stringType().optional(),
  subcircuit_id: stringType().optional()
}).describe("Warning emitted when a schematic component has a visual styling issue");
expectTypesMatch(true);
var schematic_element_outside_sheet_warning = objectType({
  type: literalType("schematic_element_outside_sheet_warning"),
  schematic_element_outside_sheet_warning_id: getZodPrefixedIdWithDefault("schematic_element_outside_sheet_warning"),
  warning_type: literalType("schematic_element_outside_sheet_warning").default("schematic_element_outside_sheet_warning"),
  message: stringType(),
  schematic_sheet_id: stringType(),
  schematic_element_type: enumType([
    "schematic_component",
    "schematic_net_label",
    "schematic_trace"
  ]),
  schematic_element_id: stringType()
}).describe("Warning emitted when a schematic component, net label, or trace extends outside its schematic sheet");
expectTypesMatch(true);
var positiveFiniteDistance = distance.pipe(numberType().positive().finite());
var schematic_graphic = objectType({
  type: literalType("schematic_graphic"),
  schematic_graphic_id: getZodPrefixedIdWithDefault("schematic_graphic"),
  schematic_sheet_id: stringType().optional(),
  asset: asset.optional(),
  svg_content: stringType().optional(),
  width: positiveFiniteDistance.optional(),
  height: positiveFiniteDistance.optional()
}).describe("References a graphic asset or inline SVG content with optional centered layout bounds on a schematic sheet").superRefine(({ asset: asset2, svg_content }, ctx) => {
  if (asset2 === undefined && svg_content === undefined) {
    ctx.addIssue({
      code: ZodIssueCode.custom,
      message: "At least one of asset or svg_content is required"
    });
  }
});
expectTypesMatch(true);
var schematic_group = objectType({
  type: literalType("schematic_group"),
  schematic_group_id: getZodPrefixedIdWithDefault("schematic_group"),
  schematic_sheet_id: stringType().optional(),
  source_group_id: stringType(),
  is_subcircuit: booleanType().optional(),
  subcircuit_id: stringType().optional(),
  width: length,
  height: length,
  center: point,
  schematic_component_ids: arrayType(stringType()),
  show_as_schematic_box: booleanType().optional(),
  name: stringType().optional(),
  description: stringType().optional()
}).describe("Defines a group of components on the schematic");
expectTypesMatch(true);
var schematic_table = objectType({
  type: literalType("schematic_table"),
  schematic_table_id: getZodPrefixedIdWithDefault("schematic_table"),
  schematic_sheet_id: stringType().optional(),
  anchor_position: point,
  column_widths: arrayType(distance),
  row_heights: arrayType(distance),
  cell_padding: distance.optional(),
  border_width: distance.optional(),
  subcircuit_id: stringType().optional(),
  schematic_component_id: stringType().optional(),
  anchor: ninePointAnchor.optional()
}).describe("Defines a table on the schematic");
expectTypesMatch(true);
var schematic_table_cell = objectType({
  type: literalType("schematic_table_cell"),
  schematic_table_cell_id: getZodPrefixedIdWithDefault("schematic_table_cell"),
  schematic_sheet_id: stringType().optional(),
  schematic_table_id: stringType(),
  start_row_index: numberType(),
  end_row_index: numberType(),
  start_column_index: numberType(),
  end_column_index: numberType(),
  text: stringType().optional(),
  center: point,
  width: distance,
  height: distance,
  horizontal_align: enumType(["left", "center", "right"]).optional(),
  vertical_align: enumType(["top", "middle", "bottom"]).optional(),
  font_size: distance.optional(),
  subcircuit_id: stringType().optional()
}).describe("Defines a cell within a schematic_table");
expectTypesMatch(true);
var schematic_sheet_size = enumType(["a4", "ansi_b"]);
var schematic_sheet = objectType({
  type: literalType("schematic_sheet"),
  schematic_sheet_id: getZodPrefixedIdWithDefault("schematic_sheet"),
  name: stringType().optional(),
  sheet_index: numberType().optional(),
  sheet_size: schematic_sheet_size.optional(),
  sheet_width: numberType().positive().optional(),
  sheet_height: numberType().positive().optional(),
  subcircuit_id: stringType().optional(),
  outline_color: stringType().optional()
}).describe("Defines a schematic sheet or page that components can be placed on");
expectTypesMatch(true);
var schematic_missing_sheet_warning = objectType({
  type: literalType("schematic_missing_sheet_warning"),
  schematic_missing_sheet_warning_id: getZodPrefixedIdWithDefault("schematic_missing_sheet_warning"),
  warning_type: literalType("schematic_missing_sheet_warning").default("schematic_missing_sheet_warning"),
  message: stringType()
}).describe("Circuit-wide warning emitted when a schematic has no schematic sheet. Display as a banner without attaching it to a component or drawing a target outline or leader line.");
expectTypesMatch(true);
var point_with_bulge = objectType({
  x: distance,
  y: distance,
  bulge: numberType().optional()
});
expectTypesMatch(true);
var ring = objectType({
  vertices: arrayType(point_with_bulge)
});
expectTypesMatch(true);
var brep_shape = objectType({
  outer_ring: ring,
  inner_rings: arrayType(ring).default([])
});
expectTypesMatch(true);
var insertionDirectionToCanonical = {
  from_left: "from_left",
  from_right: "from_right",
  from_top: "from_top",
  from_bottom: "from_bottom",
  from_above: "from_above",
  from_below: "from_below",
  from_x_neg: "from_left",
  from_x_pos: "from_right",
  from_y_pos: "from_top",
  from_y_neg: "from_bottom",
  from_z_pos: "from_above",
  from_z_neg: "from_below",
  from_front: "from_top",
  from_back: "from_bottom"
};
var insertionDirectionToVector = {
  from_left: { x: -1, y: 0, z: 0 },
  from_right: { x: 1, y: 0, z: 0 },
  from_top: { x: 0, y: 1, z: 0 },
  from_bottom: { x: 0, y: -1, z: 0 },
  from_above: { x: 0, y: 0, z: 1 },
  from_below: { x: 0, y: 0, z: -1 }
};
var insertion_direction = enumType([
  "from_left",
  "from_right",
  "from_top",
  "from_bottom",
  "from_above",
  "from_below",
  "from_x_neg",
  "from_x_pos",
  "from_y_pos",
  "from_y_neg",
  "from_z_pos",
  "from_z_neg",
  "from_front",
  "from_back"
]).transform((value) => insertionDirectionToCanonical[value]).describe('The side exposing the receptacle where the cable or mating part is attached, following the 2D PCB diagram convention, not a 3D viewport frame. In project coordinate space, "from_top" is +Y, "from_bottom" -Y, "from_left" -X, "from_right" +X, "from_above" +Z and "from_below" -Z. A receptacle on the +Y edge is "from_top" even though the plug moves in -Y as it seats. Cartesian spellings such as "from_y_pos" are accepted and normalized to the named values, as are the deprecated "from_front" (now "from_top") and "from_back" (now "from_bottom").');
expectTypesMatch(true);
expectTypesMatch(true);
var pcb_pin1_location = enumType([
  "leftside_top",
  "leftside_bottom",
  "rightside_top",
  "rightside_bottom",
  "topside_left",
  "topside_right",
  "bottomside_left",
  "bottomside_right"
]);
expectTypesMatch(true);
var pin1LocationRotationCycles = [
  [
    "leftside_top",
    "bottomside_left",
    "rightside_bottom",
    "topside_right"
  ],
  [
    "leftside_bottom",
    "bottomside_right",
    "rightside_top",
    "topside_left"
  ]
];
var getRotationBetweenPcbPin1Locations = (from, to) => {
  for (const cycle of pin1LocationRotationCycles) {
    const fromIndex = cycle.indexOf(from);
    const toIndex = cycle.indexOf(to);
    if (fromIndex !== -1 && toIndex !== -1) {
      return (toIndex - fromIndex + cycle.length) % cycle.length * 90;
    }
  }
  return null;
};
var pcb_route_hint = objectType({
  x: distance,
  y: distance,
  via: booleanType().optional(),
  via_to_layer: layer_ref.optional()
});
var pcb_route_hints = arrayType(pcb_route_hint);
expectTypesMatch(true);
expectTypesMatch(true);
var route_hint_point = objectType({
  x: distance,
  y: distance,
  via: booleanType().optional(),
  to_layer: layer_ref.optional(),
  trace_width: distance.optional()
});
expectTypesMatch(true);
var manufacturing_drc_properties = objectType({
  min_trace_width: length.optional(),
  min_board_edge_clearance: length.optional(),
  min_via_hole_edge_to_via_hole_edge_clearance: length.optional(),
  min_plated_hole_drill_edge_to_drill_edge_clearance: length.optional(),
  min_trace_to_pad_edge_clearance: length.optional(),
  min_pad_edge_to_pad_edge_clearance: length.optional(),
  min_same_net_trace_edge_to_trace_edge_clearance: length.optional(),
  min_different_net_trace_edge_to_trace_edge_clearance: length.optional(),
  min_via_edge_to_pad_edge_clearance: length.optional(),
  min_via_hole_diameter: length.optional(),
  min_via_pad_diameter: length.optional()
});
var pcb_component = objectType({
  type: literalType("pcb_component"),
  pcb_component_id: getZodPrefixedIdWithDefault("pcb_component"),
  source_component_id: stringType(),
  center: point,
  layer: layer_ref,
  rotation,
  display_offset_x: stringType().optional().describe("How to display the x offset for this part, usually corresponding with how the user specified it"),
  display_offset_y: stringType().optional().describe("How to display the y offset for this part, usually corresponding with how the user specified it"),
  width: length,
  height: length,
  do_not_place: booleanType().optional(),
  is_allowed_to_be_off_board: booleanType().optional(),
  subcircuit_id: stringType().optional(),
  pcb_group_id: stringType().optional(),
  position_mode: enumType([
    "packed",
    "relative_to_group_anchor",
    "relative_to_another_component",
    "none"
  ]).optional(),
  anchor_position: point.optional(),
  anchor_alignment: ninePointAnchor.optional(),
  positioned_relative_to_pcb_group_id: stringType().optional(),
  positioned_relative_to_pcb_board_id: stringType().optional(),
  cable_insertion_center: point.optional(),
  insertion_direction: insertion_direction.optional(),
  pin1_location: pcb_pin1_location.optional().describe("Location of pin 1 on the unrotated, top-view component footprint"),
  supplier_pin1_location_map: recordType(supplier_name, pcb_pin1_location).optional().describe("Pin 1 location for each supplier's unrotated, top-view footprint"),
  metadata: objectType({
    kicad_footprint: kicadFootprintMetadata.optional()
  }).optional(),
  obstructs_within_bounds: booleanType().default(true).describe("Does this component take up all the space within its bounds on a layer. This is generally true except for when separated pin headers are being represented by a single component (in which case, chips can be placed between the pin headers) or for tall modules where chips fit underneath")
}).describe("Defines a component on the PCB");
expectTypesMatch(true);
var pcb_debug_object_base = objectType({
  type: literalType("pcb_debug_object"),
  pcb_debug_object_id: getZodPrefixedIdWithDefault("pcb_debug_object"),
  label: stringType().optional(),
  subcircuit_id: stringType().optional()
});
var pcb_debug_rect = pcb_debug_object_base.extend({
  shape: literalType("rect"),
  center: point,
  size
});
var pcb_debug_line = pcb_debug_object_base.extend({
  shape: literalType("line"),
  start: point,
  end: point
});
var pcb_debug_point = pcb_debug_object_base.extend({
  shape: literalType("point"),
  center: point
});
var pcb_debug_object = discriminatedUnionType("shape", [
  pcb_debug_rect,
  pcb_debug_line,
  pcb_debug_point
]);
expectTypesMatch(true);
var pcb_hole_circle = objectType({
  type: literalType("pcb_hole"),
  pcb_hole_id: getZodPrefixedIdWithDefault("pcb_hole"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  pcb_component_id: stringType().optional(),
  hole_shape: literalType("circle"),
  hole_diameter: numberType(),
  x: distance,
  y: distance,
  is_covered_with_solder_mask: booleanType().optional(),
  soldermask_margin: numberType().optional()
});
var pcb_hole_circle_shape = pcb_hole_circle.describe("Defines a circular hole on the PCB");
expectTypesMatch(true);
var pcb_hole_rect = objectType({
  type: literalType("pcb_hole"),
  pcb_hole_id: getZodPrefixedIdWithDefault("pcb_hole"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  pcb_component_id: stringType().optional(),
  hole_shape: literalType("rect"),
  hole_width: numberType(),
  hole_height: numberType(),
  x: distance,
  y: distance,
  is_covered_with_solder_mask: booleanType().optional(),
  soldermask_margin: numberType().optional()
});
var pcb_hole_rect_shape = pcb_hole_rect.describe("Defines a rectangular (square-capable) hole on the PCB. Use equal width/height for square.");
expectTypesMatch(true);
var pcb_hole_circle_or_square = objectType({
  type: literalType("pcb_hole"),
  pcb_hole_id: getZodPrefixedIdWithDefault("pcb_hole"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  pcb_component_id: stringType().optional(),
  hole_shape: enumType(["circle", "square"]),
  hole_diameter: numberType(),
  x: distance,
  y: distance,
  is_covered_with_solder_mask: booleanType().optional(),
  soldermask_margin: numberType().optional()
});
var pcb_hole_circle_or_square_shape = pcb_hole_circle_or_square.describe("Defines a circular or square hole on the PCB");
expectTypesMatch(true);
var pcb_hole_oval = objectType({
  type: literalType("pcb_hole"),
  pcb_hole_id: getZodPrefixedIdWithDefault("pcb_hole"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  pcb_component_id: stringType().optional(),
  hole_shape: literalType("oval"),
  hole_width: numberType(),
  hole_height: numberType(),
  x: distance,
  y: distance,
  is_covered_with_solder_mask: booleanType().optional(),
  soldermask_margin: numberType().optional()
});
var pcb_hole_oval_shape = pcb_hole_oval.describe("Defines an oval hole on the PCB");
expectTypesMatch(true);
var pcb_hole_pill = objectType({
  type: literalType("pcb_hole"),
  pcb_hole_id: getZodPrefixedIdWithDefault("pcb_hole"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  pcb_component_id: stringType().optional(),
  hole_shape: literalType("pill"),
  hole_width: numberType(),
  hole_height: numberType(),
  x: distance,
  y: distance,
  is_covered_with_solder_mask: booleanType().optional(),
  soldermask_margin: numberType().optional()
});
var pcb_hole_pill_shape = pcb_hole_pill.describe("Defines a pill-shaped hole on the PCB");
expectTypesMatch(true);
var pcb_hole_rotated_pill = objectType({
  type: literalType("pcb_hole"),
  pcb_hole_id: getZodPrefixedIdWithDefault("pcb_hole"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  pcb_component_id: stringType().optional(),
  hole_shape: literalType("rotated_pill"),
  hole_width: numberType(),
  hole_height: numberType(),
  x: distance,
  y: distance,
  ccw_rotation: rotation,
  is_covered_with_solder_mask: booleanType().optional(),
  soldermask_margin: numberType().optional()
});
var pcb_hole_rotated_pill_shape = pcb_hole_rotated_pill.describe("Defines a rotated pill-shaped hole on the PCB");
expectTypesMatch(true);
var pcb_hole = pcb_hole_circle_or_square.or(pcb_hole_oval).or(pcb_hole_pill).or(pcb_hole_rotated_pill).or(pcb_hole_circle).or(pcb_hole_rect);
var pcb_plated_hole_circle = objectType({
  type: literalType("pcb_plated_hole"),
  shape: literalType("circle"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  outer_diameter: numberType(),
  hole_diameter: numberType(),
  is_covered_with_solder_mask: booleanType().optional(),
  x: distance,
  y: distance,
  layers: arrayType(layer_ref),
  port_hints: arrayType(stringType()).optional(),
  pcb_component_id: stringType().optional(),
  pcb_port_id: stringType().optional(),
  pcb_plated_hole_id: getZodPrefixedIdWithDefault("pcb_plated_hole"),
  soldermask_margin: numberType().optional()
});
var pcb_plated_hole_oval = objectType({
  type: literalType("pcb_plated_hole"),
  shape: enumType(["oval", "pill"]),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  outer_width: numberType(),
  outer_height: numberType(),
  hole_width: numberType(),
  hole_height: numberType(),
  is_covered_with_solder_mask: booleanType().optional(),
  x: distance,
  y: distance,
  ccw_rotation: rotation,
  layers: arrayType(layer_ref),
  port_hints: arrayType(stringType()).optional(),
  pcb_component_id: stringType().optional(),
  pcb_port_id: stringType().optional(),
  pcb_plated_hole_id: getZodPrefixedIdWithDefault("pcb_plated_hole"),
  soldermask_margin: numberType().optional()
});
var pcb_circular_hole_with_rect_pad = objectType({
  type: literalType("pcb_plated_hole"),
  shape: literalType("circular_hole_with_rect_pad"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  hole_shape: literalType("circle"),
  pad_shape: literalType("rect"),
  hole_diameter: numberType(),
  rect_pad_width: numberType(),
  rect_pad_height: numberType(),
  rect_border_radius: numberType().optional(),
  hole_offset_x: distance.default(0),
  hole_offset_y: distance.default(0),
  is_covered_with_solder_mask: booleanType().optional(),
  x: distance,
  y: distance,
  layers: arrayType(layer_ref),
  port_hints: arrayType(stringType()).optional(),
  pcb_component_id: stringType().optional(),
  pcb_port_id: stringType().optional(),
  pcb_plated_hole_id: getZodPrefixedIdWithDefault("pcb_plated_hole"),
  soldermask_margin: numberType().optional(),
  rect_ccw_rotation: rotation.optional()
});
var pcb_pill_hole_with_rect_pad = objectType({
  type: literalType("pcb_plated_hole"),
  shape: literalType("pill_hole_with_rect_pad"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  hole_shape: literalType("pill"),
  pad_shape: literalType("rect"),
  hole_width: numberType(),
  hole_height: numberType(),
  rect_pad_width: numberType(),
  rect_pad_height: numberType(),
  rect_border_radius: numberType().optional(),
  hole_offset_x: distance.default(0),
  hole_offset_y: distance.default(0),
  is_covered_with_solder_mask: booleanType().optional(),
  x: distance,
  y: distance,
  layers: arrayType(layer_ref),
  port_hints: arrayType(stringType()).optional(),
  pcb_component_id: stringType().optional(),
  pcb_port_id: stringType().optional(),
  pcb_plated_hole_id: getZodPrefixedIdWithDefault("pcb_plated_hole"),
  soldermask_margin: numberType().optional()
});
var pcb_rotated_pill_hole_with_rect_pad = objectType({
  type: literalType("pcb_plated_hole"),
  shape: literalType("rotated_pill_hole_with_rect_pad"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  hole_shape: literalType("rotated_pill"),
  pad_shape: literalType("rect"),
  hole_width: numberType(),
  hole_height: numberType(),
  hole_ccw_rotation: rotation,
  rect_pad_width: numberType(),
  rect_pad_height: numberType(),
  rect_border_radius: numberType().optional(),
  rect_ccw_rotation: rotation,
  hole_offset_x: distance.default(0),
  hole_offset_y: distance.default(0),
  is_covered_with_solder_mask: booleanType().optional(),
  x: distance,
  y: distance,
  layers: arrayType(layer_ref),
  port_hints: arrayType(stringType()).optional(),
  pcb_component_id: stringType().optional(),
  pcb_port_id: stringType().optional(),
  pcb_plated_hole_id: getZodPrefixedIdWithDefault("pcb_plated_hole"),
  soldermask_margin: numberType().optional()
});
var pcb_hole_with_polygon_pad = objectType({
  type: literalType("pcb_plated_hole"),
  shape: literalType("hole_with_polygon_pad"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  hole_shape: enumType(["circle", "oval", "pill", "rotated_pill"]),
  hole_diameter: numberType().optional(),
  hole_width: numberType().optional(),
  hole_height: numberType().optional(),
  pad_outline: arrayType(objectType({
    x: distance,
    y: distance
  })).min(3),
  hole_offset_x: distance.default(0),
  hole_offset_y: distance.default(0),
  is_covered_with_solder_mask: booleanType().optional(),
  x: distance,
  y: distance,
  layers: arrayType(layer_ref),
  port_hints: arrayType(stringType()).optional(),
  pcb_component_id: stringType().optional(),
  pcb_port_id: stringType().optional(),
  pcb_plated_hole_id: getZodPrefixedIdWithDefault("pcb_plated_hole"),
  soldermask_margin: numberType().optional(),
  ccw_rotation: rotation.optional()
});
var pcb_plated_hole = unionType([
  pcb_plated_hole_circle,
  pcb_plated_hole_oval,
  pcb_circular_hole_with_rect_pad,
  pcb_pill_hole_with_rect_pad,
  pcb_rotated_pill_hole_with_rect_pad,
  pcb_hole_with_polygon_pad
]);
expectTypesMatch(true);
expectTypesMatch(true);
expectTypesMatch(true);
expectTypesMatch(true);
expectTypesMatch(true);
expectTypesMatch(true);
var pcb_port = objectType({
  type: literalType("pcb_port"),
  pcb_port_id: getZodPrefixedIdWithDefault("pcb_port"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  source_port_id: stringType(),
  pcb_component_id: stringType().optional(),
  x: distance,
  y: distance,
  layers: arrayType(layer_ref),
  is_board_pinout: booleanType().optional()
}).describe("Defines a port on the PCB");
expectTypesMatch(true);
var pcb_smtpad_circle = objectType({
  type: literalType("pcb_smtpad"),
  shape: literalType("circle"),
  pcb_smtpad_id: getZodPrefixedIdWithDefault("pcb_smtpad"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  x: distance,
  y: distance,
  radius: numberType(),
  layer: layer_ref,
  port_hints: arrayType(stringType()).optional(),
  pcb_component_id: stringType().optional(),
  pcb_port_id: stringType().optional(),
  is_covered_with_solder_mask: booleanType().optional(),
  soldermask_margin: numberType().optional(),
  solderpaste_margin: numberType().optional()
});
var pcb_smtpad_rect = objectType({
  type: literalType("pcb_smtpad"),
  shape: literalType("rect"),
  pcb_smtpad_id: getZodPrefixedIdWithDefault("pcb_smtpad"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  x: distance,
  y: distance,
  width: numberType(),
  height: numberType(),
  rect_border_radius: numberType().optional(),
  corner_radius: numberType().optional(),
  layer: layer_ref,
  port_hints: arrayType(stringType()).optional(),
  pcb_component_id: stringType().optional(),
  pcb_port_id: stringType().optional(),
  is_covered_with_solder_mask: booleanType().optional(),
  soldermask_margin: numberType().optional(),
  soldermask_margin_left: numberType().optional(),
  soldermask_margin_top: numberType().optional(),
  soldermask_margin_right: numberType().optional(),
  soldermask_margin_bottom: numberType().optional(),
  solderpaste_margin: numberType().optional()
});
var pcb_smtpad_rotated_rect = objectType({
  type: literalType("pcb_smtpad"),
  shape: literalType("rotated_rect"),
  pcb_smtpad_id: getZodPrefixedIdWithDefault("pcb_smtpad"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  x: distance,
  y: distance,
  width: numberType(),
  height: numberType(),
  rect_border_radius: numberType().optional(),
  corner_radius: numberType().optional(),
  ccw_rotation: rotation,
  layer: layer_ref,
  port_hints: arrayType(stringType()).optional(),
  pcb_component_id: stringType().optional(),
  pcb_port_id: stringType().optional(),
  is_covered_with_solder_mask: booleanType().optional(),
  soldermask_margin: numberType().optional(),
  soldermask_margin_left: numberType().optional(),
  soldermask_margin_top: numberType().optional(),
  soldermask_margin_right: numberType().optional(),
  soldermask_margin_bottom: numberType().optional(),
  solderpaste_margin: numberType().optional()
});
var pcb_smtpad_pill = objectType({
  type: literalType("pcb_smtpad"),
  shape: literalType("pill"),
  pcb_smtpad_id: getZodPrefixedIdWithDefault("pcb_smtpad"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  x: distance,
  y: distance,
  width: numberType(),
  height: numberType(),
  radius: numberType(),
  layer: layer_ref,
  port_hints: arrayType(stringType()).optional(),
  pcb_component_id: stringType().optional(),
  pcb_port_id: stringType().optional(),
  is_covered_with_solder_mask: booleanType().optional(),
  soldermask_margin: numberType().optional(),
  solderpaste_margin: numberType().optional()
});
var pcb_smtpad_rotated_pill = objectType({
  type: literalType("pcb_smtpad"),
  shape: literalType("rotated_pill"),
  pcb_smtpad_id: getZodPrefixedIdWithDefault("pcb_smtpad"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  x: distance,
  y: distance,
  width: numberType(),
  height: numberType(),
  radius: numberType(),
  ccw_rotation: rotation,
  layer: layer_ref,
  port_hints: arrayType(stringType()).optional(),
  pcb_component_id: stringType().optional(),
  pcb_port_id: stringType().optional(),
  is_covered_with_solder_mask: booleanType().optional(),
  soldermask_margin: numberType().optional(),
  solderpaste_margin: numberType().optional()
});
var pcb_smtpad_polygon = objectType({
  type: literalType("pcb_smtpad"),
  shape: literalType("polygon"),
  pcb_smtpad_id: getZodPrefixedIdWithDefault("pcb_smtpad"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  points: arrayType(point),
  layer: layer_ref,
  port_hints: arrayType(stringType()).optional(),
  pcb_component_id: stringType().optional(),
  pcb_port_id: stringType().optional(),
  is_covered_with_solder_mask: booleanType().optional(),
  soldermask_margin: numberType().optional(),
  solderpaste_margin: numberType().optional()
});
var pcb_smtpad = discriminatedUnionType("shape", [
  pcb_smtpad_circle,
  pcb_smtpad_rect,
  pcb_smtpad_rotated_rect,
  pcb_smtpad_rotated_pill,
  pcb_smtpad_pill,
  pcb_smtpad_polygon
]).describe("Defines an SMT pad on the PCB");
expectTypesMatch(true);
expectTypesMatch(true);
expectTypesMatch(true);
expectTypesMatch(true);
expectTypesMatch(true);
expectTypesMatch(true);
var pcb_solder_paste_circle = objectType({
  type: literalType("pcb_solder_paste"),
  shape: literalType("circle"),
  pcb_solder_paste_id: getZodPrefixedIdWithDefault("pcb_solder_paste"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  x: distance,
  y: distance,
  radius: numberType(),
  layer: layer_ref,
  pcb_component_id: stringType().optional(),
  pcb_smtpad_id: stringType().optional()
});
var pcb_solder_paste_rect = objectType({
  type: literalType("pcb_solder_paste"),
  shape: literalType("rect"),
  pcb_solder_paste_id: getZodPrefixedIdWithDefault("pcb_solder_paste"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  x: distance,
  y: distance,
  width: numberType(),
  height: numberType(),
  layer: layer_ref,
  pcb_component_id: stringType().optional(),
  pcb_smtpad_id: stringType().optional()
});
var pcb_solder_paste_pill = objectType({
  type: literalType("pcb_solder_paste"),
  shape: literalType("pill"),
  pcb_solder_paste_id: getZodPrefixedIdWithDefault("pcb_solder_paste"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  x: distance,
  y: distance,
  width: numberType(),
  height: numberType(),
  radius: numberType(),
  layer: layer_ref,
  pcb_component_id: stringType().optional(),
  pcb_smtpad_id: stringType().optional()
});
var pcb_solder_paste_rotated_rect = objectType({
  type: literalType("pcb_solder_paste"),
  shape: literalType("rotated_rect"),
  pcb_solder_paste_id: getZodPrefixedIdWithDefault("pcb_solder_paste"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  x: distance,
  y: distance,
  width: numberType(),
  height: numberType(),
  ccw_rotation: distance,
  layer: layer_ref,
  pcb_component_id: stringType().optional(),
  pcb_smtpad_id: stringType().optional()
});
var pcb_solder_paste_rotated_pill = objectType({
  type: literalType("pcb_solder_paste"),
  shape: literalType("rotated_pill"),
  pcb_solder_paste_id: getZodPrefixedIdWithDefault("pcb_solder_paste"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  x: distance,
  y: distance,
  width: numberType(),
  height: numberType(),
  radius: numberType(),
  ccw_rotation: rotation,
  layer: layer_ref,
  pcb_component_id: stringType().optional(),
  pcb_smtpad_id: stringType().optional()
});
var pcb_solder_paste_oval = objectType({
  type: literalType("pcb_solder_paste"),
  shape: literalType("oval"),
  pcb_solder_paste_id: getZodPrefixedIdWithDefault("pcb_solder_paste"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  x: distance,
  y: distance,
  width: numberType(),
  height: numberType(),
  layer: layer_ref,
  pcb_component_id: stringType().optional(),
  pcb_smtpad_id: stringType().optional()
});
var pcb_solder_paste = unionType([
  pcb_solder_paste_circle,
  pcb_solder_paste_rect,
  pcb_solder_paste_pill,
  pcb_solder_paste_rotated_rect,
  pcb_solder_paste_rotated_pill,
  pcb_solder_paste_oval
]).describe("Defines solderpaste on the PCB");
expectTypesMatch(true);
expectTypesMatch(true);
expectTypesMatch(true);
expectTypesMatch(true);
expectTypesMatch(true);
expectTypesMatch(true);
var pcb_text = objectType({
  type: literalType("pcb_text"),
  pcb_text_id: getZodPrefixedIdWithDefault("pcb_text"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  text: stringType(),
  center: point,
  layer: layer_ref,
  width: length,
  height: length,
  lines: numberType(),
  align: enumType(["bottom-left"])
}).describe("Defines text on the PCB");
expectTypesMatch(true);
var pcb_trace_route_point_wire = objectType({
  route_type: literalType("wire"),
  x: distance,
  y: distance,
  width: distance,
  copper_pour_id: stringType().optional(),
  is_inside_copper_pour: booleanType().optional(),
  start_pcb_port_id: stringType().optional(),
  end_pcb_port_id: stringType().optional(),
  layer: layer_ref
});
var pcb_trace_route_point_via = objectType({
  route_type: literalType("via"),
  x: distance,
  y: distance,
  copper_pour_id: stringType().optional(),
  is_inside_copper_pour: booleanType().optional(),
  hole_diameter: distance.optional(),
  outer_diameter: distance.optional(),
  tented_on_top: booleanType().optional(),
  tented_on_bottom: booleanType().optional(),
  from_layer: layer_ref,
  to_layer: layer_ref
});
var pcb_trace_route_point_through_pad = objectType({
  route_type: literalType("through_pad"),
  start: point,
  end: point,
  width: distance,
  start_layer: layer_ref,
  end_layer: layer_ref,
  pcb_smtpad_id: stringType().optional(),
  pcb_plated_hole_id: stringType().optional()
});
var pcb_trace_route_point = unionType([
  pcb_trace_route_point_wire,
  pcb_trace_route_point_via,
  pcb_trace_route_point_through_pad
]);
var pcb_trace = objectType({
  type: literalType("pcb_trace"),
  source_trace_id: stringType().optional(),
  pcb_component_id: stringType().optional(),
  pcb_trace_id: getZodPrefixedIdWithDefault("pcb_trace"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  route_thickness_mode: enumType(["constant", "interpolated"]).default("constant").optional(),
  route_order_index: numberType().optional(),
  should_round_corners: booleanType().optional(),
  trace_length: numberType().optional(),
  highlight_color: stringType().optional(),
  route: arrayType(pcb_trace_route_point)
}).describe("Defines a trace on the PCB");
expectTypesMatch(true);
expectTypesMatch(true);
var pcb_trace_warning = objectType({
  type: literalType("pcb_trace_warning"),
  pcb_trace_warning_id: getZodPrefixedIdWithDefault("pcb_trace_warning"),
  warning_type: literalType("pcb_trace_warning").default("pcb_trace_warning"),
  message: stringType(),
  center: point.optional(),
  pcb_trace_id: stringType(),
  source_trace_id: stringType(),
  pcb_component_ids: arrayType(stringType()),
  pcb_port_ids: arrayType(stringType()),
  subcircuit_id: stringType().optional()
}).describe("Defines a trace warning on the PCB");
expectTypesMatch(true);
var pcb_trace_too_long_error = objectType({
  type: literalType("pcb_trace_too_long_error"),
  pcb_trace_too_long_error_id: getZodPrefixedIdWithDefault("pcb_trace_too_long_error"),
  error_type: literalType("pcb_trace_too_long_error").default("pcb_trace_too_long_error"),
  message: stringType(),
  pcb_trace_id: stringType(),
  source_net_id: stringType().optional(),
  source_trace_id: stringType().optional(),
  actual_trace_length: distance,
  maximum_trace_length: distance,
  subcircuit_id: stringType().optional()
}).describe("Error emitted when a PCB trace is longer than its maximum allowed length");
expectTypesMatch(true);
var pcb_bus_length_skew_error = base_circuit_json_error.extend({
  type: literalType("pcb_bus_length_skew_error"),
  pcb_bus_length_skew_error_id: getZodPrefixedIdWithDefault("pcb_bus_length_skew_error"),
  error_type: literalType("pcb_bus_length_skew_error").default("pcb_bus_length_skew_error"),
  source_bus_id: stringType(),
  source_trace_ids: arrayType(stringType()),
  pcb_trace_ids: arrayType(stringType()),
  actual_length_skew: numberType().nonnegative().finite(),
  maximum_length_skew: numberType().nonnegative().finite(),
  subcircuit_id: stringType().optional()
});
expectTypesMatch(true);
var pcb_trace_too_long_warning = objectType({
  type: literalType("pcb_trace_too_long_warning"),
  pcb_trace_too_long_warning_id: getZodPrefixedIdWithDefault("pcb_trace_too_long_warning"),
  warning_type: literalType("pcb_trace_too_long_warning").default("pcb_trace_too_long_warning"),
  message: stringType(),
  pcb_trace_id: stringType(),
  source_net_id: stringType().optional(),
  source_trace_id: stringType().optional(),
  actual_trace_length: distance,
  maximum_trace_length: distance,
  subcircuit_id: stringType().optional()
}).describe("Warning emitted when a PCB trace is longer than its maximum allowed length");
expectTypesMatch(true);
var pcb_trace_too_many_vias_warning = objectType({
  type: literalType("pcb_trace_too_many_vias_warning"),
  pcb_trace_too_many_vias_warning_id: getZodPrefixedIdWithDefault("pcb_trace_too_many_vias_warning"),
  warning_type: literalType("pcb_trace_too_many_vias_warning").default("pcb_trace_too_many_vias_warning"),
  message: stringType(),
  pcb_trace_id: stringType(),
  source_net_id: stringType().optional(),
  source_trace_id: stringType().optional(),
  actual_via_count: numberType().int().nonnegative(),
  maximum_via_count: numberType().int().nonnegative(),
  subcircuit_id: stringType().optional()
}).describe("Warning emitted when a PCB trace has more vias than its maximum allowed count");
expectTypesMatch(true);
var pcb_trace_error = base_circuit_json_error.extend({
  type: literalType("pcb_trace_error"),
  pcb_trace_error_id: getZodPrefixedIdWithDefault("pcb_trace_error"),
  error_type: literalType("pcb_trace_error").default("pcb_trace_error"),
  center: point.optional(),
  pcb_trace_id: stringType(),
  source_trace_id: stringType(),
  pcb_component_ids: arrayType(stringType()),
  pcb_port_ids: arrayType(stringType()),
  subcircuit_id: stringType().optional()
}).describe("Defines a trace error on the PCB");
expectTypesMatch(true);
var pcb_trace_missing_error = base_circuit_json_error.extend({
  type: literalType("pcb_trace_missing_error"),
  pcb_trace_missing_error_id: getZodPrefixedIdWithDefault("pcb_trace_missing_error"),
  error_type: literalType("pcb_trace_missing_error").default("pcb_trace_missing_error"),
  center: point.optional(),
  source_trace_id: stringType(),
  pcb_component_ids: arrayType(stringType()),
  pcb_port_ids: arrayType(stringType()),
  subcircuit_id: stringType().optional()
}).describe("Defines an error when a source trace has no corresponding PCB trace");
expectTypesMatch(true);
var pcb_port_not_matched_error = base_circuit_json_error.extend({
  type: literalType("pcb_port_not_matched_error"),
  pcb_error_id: getZodPrefixedIdWithDefault("pcb_error"),
  error_type: literalType("pcb_port_not_matched_error").default("pcb_port_not_matched_error"),
  pcb_component_ids: arrayType(stringType()),
  subcircuit_id: stringType().optional()
}).describe("Defines a trace error on the PCB where a port is not matched");
expectTypesMatch(true);
var pcb_port_not_connected_error = base_circuit_json_error.extend({
  type: literalType("pcb_port_not_connected_error"),
  pcb_port_not_connected_error_id: getZodPrefixedIdWithDefault("pcb_port_not_connected_error"),
  error_type: literalType("pcb_port_not_connected_error").default("pcb_port_not_connected_error"),
  pcb_port_ids: arrayType(stringType()),
  pcb_component_ids: arrayType(stringType()),
  subcircuit_id: stringType().optional()
}).describe("Defines an error when a pcb port is not connected to any trace");
expectTypesMatch(true);
var pcb_net = objectType({
  type: literalType("pcb_net"),
  pcb_net_id: getZodPrefixedIdWithDefault("pcb_net"),
  source_net_id: stringType().optional(),
  highlight_color: stringType().optional()
}).describe("Defines a net on the PCB");
expectTypesMatch(true);
var pcb_via = objectType({
  type: literalType("pcb_via"),
  pcb_via_id: getZodPrefixedIdWithDefault("pcb_via"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  subcircuit_connectivity_map_key: stringType().optional(),
  x: distance,
  y: distance,
  outer_diameter: distance.default("0.6mm"),
  hole_diameter: distance.default("0.25mm"),
  topmost_drill_layer: layer_ref.optional(),
  bottommost_drill_layer: layer_ref.optional(),
  through_hole: booleanType().optional(),
  from_layer: layer_ref.optional(),
  to_layer: layer_ref.optional(),
  layers: arrayType(layer_ref),
  pcb_port_ids: arrayType(stringType()).optional(),
  pcb_trace_id: stringType().optional(),
  source_trace_id: stringType().optional(),
  source_net_id: stringType().min(1).optional(),
  net_is_assignable: booleanType().optional(),
  net_assigned: booleanType().optional(),
  is_tented: booleanType().optional(),
  tented_on_top: booleanType().optional(),
  tented_on_bottom: booleanType().optional()
}).transform(({ is_tented, ...via }) => {
  if (is_tented !== undefined) {
    via.tented_on_top ??= is_tented;
    via.tented_on_bottom ??= is_tented;
  }
  return via;
}).describe("Defines a via on the PCB");
expectTypesMatch(true);
var pcb_board = objectType({
  type: literalType("pcb_board"),
  pcb_board_id: getZodPrefixedIdWithDefault("pcb_board"),
  pcb_panel_id: stringType().optional(),
  carrier_pcb_board_id: stringType().optional(),
  is_subcircuit: booleanType().optional(),
  subcircuit_id: stringType().optional(),
  is_mounted_to_carrier_board: booleanType().optional(),
  is_via_in_pad_allowed: booleanType().optional(),
  default_via_tented_on_top: booleanType().optional(),
  default_via_tented_on_bottom: booleanType().optional(),
  width: length.optional(),
  height: length.optional(),
  center: point,
  display_offset_x: stringType().optional().describe("How to display the x offset for this board, usually corresponding with how the user specified it"),
  display_offset_y: stringType().optional().describe("How to display the y offset for this board, usually corresponding with how the user specified it"),
  thickness: length.optional().default(1.4),
  num_layers: numberType().optional().default(4),
  allow_blind_and_buried_vias: booleanType().optional().describe("Whether autorouters may generate blind and buried vias. False restricts newly generated vias to the full board stack."),
  outline: arrayType(point).optional(),
  shape: enumType(["rect", "polygon"]).optional(),
  material: enumType(["fr4", "fr1", "flex"]).default("fr4"),
  solder_mask_color: stringType().optional(),
  silkscreen_color: stringType().optional(),
  anchor_position: point.optional(),
  anchor_alignment: ninePointAnchor.optional(),
  position_mode: enumType(["relative_to_panel_anchor", "none"]).optional()
}).merge(manufacturing_drc_properties).describe("Defines the board outline of the PCB");
expectTypesMatch(true);
var finite_point = point.extend({
  x: length.pipe(numberType().finite()),
  y: length.pipe(numberType().finite())
});
var pcb_bend = objectType({
  type: literalType("pcb_bend"),
  pcb_bend_id: getZodPrefixedIdWithDefault("pcb_bend"),
  pcb_board_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  name: stringType().optional(),
  start: finite_point,
  end: finite_point,
  bend_angle: rotation.pipe(numberType().finite()),
  bend_radius: length.pipe(numberType().finite().positive()),
  bend_side: enumType(["left", "right"])
}).refine(({ start, end }) => start.x !== end.x || start.y !== end.y, {
  message: "Bend centerline endpoints must be distinct",
  path: ["end"]
}).describe("Defines a finite-radius bend on a flat PCB for runtime CAD folding");
expectTypesMatch(true);
var positive_length = length.pipe(numberType().finite().positive());
var finite_point2 = point.extend({
  x: length.pipe(numberType().finite()),
  y: length.pipe(numberType().finite())
});
var pcb_stiffener_base = objectType({
  type: literalType("pcb_stiffener"),
  pcb_stiffener_id: getZodPrefixedIdWithDefault("pcb_stiffener"),
  pcb_board_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  name: stringType().optional(),
  layer: enumType(["top", "bottom"]),
  material: enumType(["fr4", "polyimide", "stainless_steel", "aluminum"]),
  thickness: positive_length,
  adhesive_thickness: length.pipe(numberType().finite().nonnegative()).optional()
});
var pcb_stiffener_rect = pcb_stiffener_base.extend({
  shape: literalType("rect"),
  center: finite_point2,
  rotation: rotation.pipe(numberType().finite()).optional(),
  width: positive_length,
  height: positive_length,
  outline: neverType().optional()
});
expectTypesMatch(true);
var pcb_stiffener_polygon = pcb_stiffener_base.extend({
  shape: literalType("polygon"),
  outline: arrayType(finite_point2).min(3).refine((points) => {
    const twice_area = points.reduce((sum, p, i) => {
      const next = points[(i + 1) % points.length];
      return sum + p.x * next.y - next.x * p.y;
    }, 0);
    return Number.isFinite(twice_area) && twice_area !== 0;
  }, "Stiffener outline must enclose a nonzero area"),
  center: neverType().optional(),
  rotation: neverType().optional(),
  width: neverType().optional(),
  height: neverType().optional()
});
expectTypesMatch(true);
var pcb_stiffener = discriminatedUnionType("shape", [pcb_stiffener_rect, pcb_stiffener_polygon]).describe("Defines bonded mechanical PCB reinforcement without adding copper layers");
expectTypesMatch(true);
var pcb_panel = objectType({
  type: literalType("pcb_panel"),
  pcb_panel_id: getZodPrefixedIdWithDefault("pcb_panel"),
  width: length,
  height: length,
  center: point,
  thickness: length.optional().default(1.4),
  covered_with_solder_mask: booleanType().optional().default(true)
}).describe("Defines a PCB panel that can contain multiple boards");
expectTypesMatch(true);
var pcb_placement_error = base_circuit_json_error.extend({
  type: literalType("pcb_placement_error"),
  pcb_placement_error_id: getZodPrefixedIdWithDefault("pcb_placement_error"),
  error_type: literalType("pcb_placement_error").default("pcb_placement_error"),
  subcircuit_id: stringType().optional()
}).describe("Defines a placement error on the PCB");
expectTypesMatch(true);
var pcb_packing_error = base_circuit_json_error.extend({
  type: literalType("pcb_packing_error"),
  pcb_packing_error_id: getZodPrefixedIdWithDefault("pcb_packing_error"),
  error_type: literalType("pcb_packing_error").default("pcb_packing_error"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional()
}).describe("Defines a failure to pack PCB components within layout bounds");
expectTypesMatch(true);
var pcb_panelization_placement_error = base_circuit_json_error.extend({
  type: literalType("pcb_panelization_placement_error"),
  pcb_panelization_placement_error_id: getZodPrefixedIdWithDefault("pcb_panelization_placement_error"),
  error_type: literalType("pcb_panelization_placement_error").default("pcb_panelization_placement_error"),
  pcb_panel_id: stringType().optional(),
  pcb_board_id: stringType().optional(),
  subcircuit_id: stringType().optional()
}).describe("Defines a panelization placement error on the PCB");
expectTypesMatch(true);
var pcb_trace_hint = objectType({
  type: literalType("pcb_trace_hint"),
  pcb_trace_hint_id: getZodPrefixedIdWithDefault("pcb_trace_hint"),
  pcb_port_id: stringType(),
  pcb_component_id: stringType(),
  route: arrayType(route_hint_point),
  subcircuit_id: stringType().optional()
}).describe("A hint that can be used during generation of a PCB trace");
expectTypesMatch(true);
var pcb_silkscreen_line = objectType({
  type: literalType("pcb_silkscreen_line"),
  pcb_silkscreen_line_id: getZodPrefixedIdWithDefault("pcb_silkscreen_line"),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  stroke_width: distance.default("0.1mm"),
  x1: distance,
  y1: distance,
  x2: distance,
  y2: distance,
  layer: visible_layer
}).describe("Defines a silkscreen line on the PCB");
expectTypesMatch(true);
var pcb_silkscreen_path = objectType({
  type: literalType("pcb_silkscreen_path"),
  pcb_silkscreen_path_id: getZodPrefixedIdWithDefault("pcb_silkscreen_path"),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  layer: visible_layer,
  route: arrayType(point),
  stroke_width: length
}).describe("Defines a silkscreen path on the PCB");
expectTypesMatch(true);
var pcb_silkscreen_text = objectType({
  type: literalType("pcb_silkscreen_text"),
  pcb_silkscreen_text_id: getZodPrefixedIdWithDefault("pcb_silkscreen_text"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  font: literalType("tscircuit2024").default("tscircuit2024"),
  font_size: distance.default("0.2mm"),
  pcb_component_id: stringType(),
  text: stringType(),
  is_knockout: booleanType().default(false).optional(),
  knockout_padding: objectType({
    left: length,
    top: length,
    bottom: length,
    right: length
  }).default({
    left: "0.2mm",
    top: "0.2mm",
    bottom: "0.2mm",
    right: "0.2mm"
  }).optional(),
  ccw_rotation: numberType().optional(),
  layer: layer_ref,
  is_mirrored: booleanType().default(false).optional(),
  anchor_position: point.default({ x: 0, y: 0 }),
  anchor_alignment: ninePointAnchor.default("center")
}).describe("Defines silkscreen text on the PCB");
expectTypesMatch(true);
var pcb_copper_text = objectType({
  type: literalType("pcb_copper_text"),
  pcb_copper_text_id: getZodPrefixedIdWithDefault("pcb_copper_text"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  font: literalType("tscircuit2024").default("tscircuit2024"),
  font_size: distance.default("0.2mm"),
  pcb_component_id: stringType(),
  text: stringType(),
  is_knockout: booleanType().default(false).optional(),
  knockout_padding: objectType({
    left: length,
    top: length,
    bottom: length,
    right: length
  }).default({
    left: "0.2mm",
    top: "0.2mm",
    bottom: "0.2mm",
    right: "0.2mm"
  }).optional(),
  ccw_rotation: numberType().optional(),
  layer: layer_ref,
  is_mirrored: booleanType().default(false).optional(),
  anchor_position: point.default({ x: 0, y: 0 }),
  anchor_alignment: ninePointAnchor.default("center")
}).describe("Defines copper text on the PCB");
expectTypesMatch(true);
var pcb_silkscreen_rect = objectType({
  type: literalType("pcb_silkscreen_rect"),
  pcb_silkscreen_rect_id: getZodPrefixedIdWithDefault("pcb_silkscreen_rect"),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  center: point,
  width: length,
  height: length,
  layer: layer_ref,
  stroke_width: length.default("1mm"),
  corner_radius: length.optional(),
  is_filled: booleanType().default(true).optional(),
  has_stroke: booleanType().optional(),
  is_stroke_dashed: booleanType().optional(),
  ccw_rotation: numberType().optional()
}).describe("Defines a silkscreen rect on the PCB");
expectTypesMatch(true);
var pcb_silkscreen_circle = objectType({
  type: literalType("pcb_silkscreen_circle"),
  pcb_silkscreen_circle_id: getZodPrefixedIdWithDefault("pcb_silkscreen_circle"),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  center: point,
  radius: length,
  layer: visible_layer,
  stroke_width: length.default("1mm"),
  is_filled: booleanType().optional()
}).describe("Defines a silkscreen circle on the PCB");
expectTypesMatch(true);
var pcb_silkscreen_oval = objectType({
  type: literalType("pcb_silkscreen_oval"),
  pcb_silkscreen_oval_id: getZodPrefixedIdWithDefault("pcb_silkscreen_oval"),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  center: point,
  radius_x: distance,
  radius_y: distance,
  layer: visible_layer,
  ccw_rotation: rotation.optional()
}).describe("Defines a silkscreen oval on the PCB");
expectTypesMatch(true);
var pcb_silkscreen_graphic_base = objectType({
  type: literalType("pcb_silkscreen_graphic"),
  pcb_silkscreen_graphic_id: getZodPrefixedIdWithDefault("pcb_silkscreen_graphic"),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  layer: visible_layer,
  image_asset: asset.optional()
});
var pcb_silkscreen_graphic_brep = pcb_silkscreen_graphic_base.extend({
  shape: literalType("brep"),
  brep_shape
}).describe("Defines a BRep silkscreen graphic on the PCB");
expectTypesMatch(true);
var pcb_silkscreen_graphic = discriminatedUnionType("shape", [pcb_silkscreen_graphic_brep]).describe("Defines a silkscreen graphic on the PCB");
expectTypesMatch(true);
var pcb_silkscreen_pill = objectType({
  type: literalType("pcb_silkscreen_pill"),
  pcb_silkscreen_pill_id: getZodPrefixedIdWithDefault("pcb_silkscreen_pill"),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  center: point,
  width: length,
  height: length,
  layer: layer_ref,
  ccw_rotation: numberType().optional()
}).describe("Defines a silkscreen pill on the PCB");
expectTypesMatch(true);
var pcb_fabrication_note_text = objectType({
  type: literalType("pcb_fabrication_note_text"),
  pcb_fabrication_note_text_id: getZodPrefixedIdWithDefault("pcb_fabrication_note_text"),
  subcircuit_id: stringType().optional(),
  pcb_group_id: stringType().optional(),
  font: literalType("tscircuit2024").default("tscircuit2024"),
  font_size: distance.default("1mm"),
  pcb_component_id: stringType(),
  text: stringType(),
  ccw_rotation: numberType().optional(),
  layer: visible_layer,
  anchor_position: point.default({ x: 0, y: 0 }),
  anchor_alignment: enumType(["center", "top_left", "top_right", "bottom_left", "bottom_right"]).default("center"),
  color: stringType().optional()
}).describe("Defines a fabrication note in text on the PCB, useful for leaving notes for assemblers or fabricators");
expectTypesMatch(true);
var pcb_fabrication_note_path = objectType({
  type: literalType("pcb_fabrication_note_path"),
  pcb_fabrication_note_path_id: getZodPrefixedIdWithDefault("pcb_fabrication_note_path"),
  pcb_component_id: stringType(),
  subcircuit_id: stringType().optional(),
  layer: layer_ref,
  route: arrayType(point),
  stroke_width: length,
  color: stringType().optional()
}).describe("Defines a fabrication path on the PCB for fabricators or assemblers");
expectTypesMatch(true);
var pcb_fabrication_note_rect = objectType({
  type: literalType("pcb_fabrication_note_rect"),
  pcb_fabrication_note_rect_id: getZodPrefixedIdWithDefault("pcb_fabrication_note_rect"),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  center: point,
  width: length,
  height: length,
  layer: visible_layer,
  stroke_width: length.default("0.1mm"),
  corner_radius: length.optional(),
  is_filled: booleanType().optional(),
  has_stroke: booleanType().optional(),
  is_stroke_dashed: booleanType().optional(),
  color: stringType().optional()
}).describe("Defines a fabrication note rectangle on the PCB");
expectTypesMatch(true);
var pcb_fabrication_note_dimension = objectType({
  type: literalType("pcb_fabrication_note_dimension"),
  pcb_fabrication_note_dimension_id: getZodPrefixedIdWithDefault("pcb_fabrication_note_dimension"),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  layer: visible_layer,
  from: point,
  to: point,
  text: stringType().optional(),
  text_ccw_rotation: numberType().optional(),
  offset: length.optional(),
  offset_distance: length.optional(),
  offset_direction: objectType({
    x: numberType(),
    y: numberType()
  }).optional(),
  font: literalType("tscircuit2024").default("tscircuit2024"),
  font_size: length.default("1mm"),
  color: stringType().optional(),
  arrow_size: length.default("1mm")
}).describe("Defines a measurement annotation within PCB fabrication notes");
expectTypesMatch(true);
var pcb_note_text = objectType({
  type: literalType("pcb_note_text"),
  pcb_note_text_id: getZodPrefixedIdWithDefault("pcb_note_text"),
  pcb_component_id: stringType().optional(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  name: stringType().optional(),
  font: literalType("tscircuit2024").default("tscircuit2024"),
  font_size: distance.default("1mm"),
  text: stringType().optional(),
  anchor_position: point.default({ x: 0, y: 0 }),
  anchor_alignment: enumType(["center", "top_left", "top_right", "bottom_left", "bottom_right"]).default("center"),
  layer: visible_layer.default("top"),
  is_mirrored_from_top_view: booleanType().optional(),
  color: stringType().optional()
}).describe("Defines a documentation note in text on the PCB");
expectTypesMatch(true);
var pcb_note_rect = objectType({
  type: literalType("pcb_note_rect"),
  pcb_note_rect_id: getZodPrefixedIdWithDefault("pcb_note_rect"),
  pcb_component_id: stringType().optional(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  name: stringType().optional(),
  text: stringType().optional(),
  center: point,
  width: length,
  height: length,
  layer: visible_layer.default("top"),
  stroke_width: length.default("0.1mm"),
  corner_radius: length.optional(),
  is_filled: booleanType().optional(),
  has_stroke: booleanType().optional(),
  is_stroke_dashed: booleanType().optional(),
  color: stringType().optional()
}).describe("Defines a rectangular documentation note on the PCB");
expectTypesMatch(true);
var pcb_note_path = objectType({
  type: literalType("pcb_note_path"),
  pcb_note_path_id: getZodPrefixedIdWithDefault("pcb_note_path"),
  pcb_component_id: stringType().optional(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  name: stringType().optional(),
  text: stringType().optional(),
  route: arrayType(point),
  layer: visible_layer.default("top"),
  stroke_width: length.default("0.1mm"),
  color: stringType().optional()
}).describe("Defines a polyline documentation note on the PCB");
expectTypesMatch(true);
var pcb_note_line = objectType({
  type: literalType("pcb_note_line"),
  pcb_note_line_id: getZodPrefixedIdWithDefault("pcb_note_line"),
  pcb_component_id: stringType().optional(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  name: stringType().optional(),
  text: stringType().optional(),
  x1: distance,
  y1: distance,
  x2: distance,
  y2: distance,
  layer: visible_layer.default("top"),
  stroke_width: distance.default("0.1mm"),
  color: stringType().optional(),
  is_dashed: booleanType().optional()
}).describe("Defines a straight documentation note line on the PCB");
expectTypesMatch(true);
var pcb_note_dimension = objectType({
  type: literalType("pcb_note_dimension"),
  pcb_note_dimension_id: getZodPrefixedIdWithDefault("pcb_note_dimension"),
  pcb_component_id: stringType().optional(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  name: stringType().optional(),
  from: point,
  to: point,
  text: stringType().optional(),
  text_ccw_rotation: numberType().optional(),
  offset_distance: length.optional(),
  offset_direction: objectType({
    x: numberType(),
    y: numberType()
  }).optional(),
  font: literalType("tscircuit2024").default("tscircuit2024"),
  font_size: length.default("1mm"),
  layer: visible_layer.default("top"),
  color: stringType().optional(),
  arrow_size: length.default("1mm")
}).describe("Defines a measurement annotation within PCB documentation notes");
expectTypesMatch(true);
var pcb_footprint_overlap_error = base_circuit_json_error.extend({
  type: literalType("pcb_footprint_overlap_error"),
  pcb_error_id: getZodPrefixedIdWithDefault("pcb_error"),
  error_type: literalType("pcb_footprint_overlap_error").default("pcb_footprint_overlap_error"),
  pcb_smtpad_ids: arrayType(stringType()).optional(),
  pcb_plated_hole_ids: arrayType(stringType()).optional(),
  pcb_hole_ids: arrayType(stringType()).optional(),
  pcb_keepout_ids: arrayType(stringType()).optional()
}).describe("Error emitted when a pcb footprint overlaps with another element");
expectTypesMatch(true);
var pcb_courtyard_overlap_error = base_circuit_json_error.extend({
  type: literalType("pcb_courtyard_overlap_error"),
  pcb_error_id: getZodPrefixedIdWithDefault("pcb_error"),
  error_type: literalType("pcb_courtyard_overlap_error").default("pcb_courtyard_overlap_error"),
  pcb_component_ids: tupleType([stringType(), stringType()])
}).describe("Error emitted when the courtyard (CrtYd) of one PCB component overlaps with the courtyard of another");
expectTypesMatch(true);
var pcb_keepout_outline = objectType({
  type: literalType("pcb_keepout"),
  shape: literalType("outline"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  outline: arrayType(point).min(2),
  stroke_width: length,
  pcb_keepout_id: stringType(),
  layers: arrayType(stringType()),
  description: stringType().optional(),
  excluded_pcb_component_ids: arrayType(stringType()).optional(),
  warning_only: booleanType().optional(),
  allow_traces: booleanType().optional(),
  allow_placements: booleanType().optional()
});
var pcb_keepout = objectType({
  type: literalType("pcb_keepout"),
  shape: literalType("rect"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  center: point,
  width: distance,
  height: distance,
  pcb_keepout_id: stringType(),
  layers: arrayType(stringType()),
  description: stringType().optional(),
  excluded_pcb_component_ids: arrayType(stringType()).optional(),
  warning_only: booleanType().optional(),
  allow_traces: booleanType().optional(),
  allow_placements: booleanType().optional()
}).or(objectType({
  type: literalType("pcb_keepout"),
  shape: literalType("circle"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  center: point,
  radius: distance,
  pcb_keepout_id: stringType(),
  layers: arrayType(stringType()),
  description: stringType().optional(),
  excluded_pcb_component_ids: arrayType(stringType()).optional(),
  warning_only: booleanType().optional(),
  allow_traces: booleanType().optional(),
  allow_placements: booleanType().optional()
})).or(pcb_keepout_outline);
expectTypesMatch(true);
expectTypesMatch(true);
var pcb_keepout_overlap_warning = objectType({
  type: literalType("pcb_keepout_overlap_warning"),
  pcb_keepout_overlap_warning_id: getZodPrefixedIdWithDefault("pcb_keepout_overlap_warning"),
  warning_type: literalType("pcb_keepout_overlap_warning").default("pcb_keepout_overlap_warning"),
  message: stringType(),
  pcb_keepout_id: stringType(),
  pcb_component_ids: arrayType(stringType()).optional(),
  pcb_trace_ids: arrayType(stringType()).optional(),
  pcb_smtpad_ids: arrayType(stringType()).optional(),
  pcb_plated_hole_ids: arrayType(stringType()).optional(),
  pcb_via_ids: arrayType(stringType()).optional(),
  center: point.optional(),
  subcircuit_id: stringType().optional()
}).describe("Warning emitted when copper overlaps a PCB keepout with warning_only enabled");
expectTypesMatch(true);
var pcb_cutout_base = objectType({
  type: literalType("pcb_cutout"),
  pcb_cutout_id: getZodPrefixedIdWithDefault("pcb_cutout"),
  pcb_component_id: stringType().optional(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  pcb_board_id: stringType().optional(),
  pcb_panel_id: stringType().optional()
});
var pcb_cutout_rect = pcb_cutout_base.extend({
  shape: literalType("rect"),
  center: point,
  width: length,
  height: length,
  rotation: rotation.optional(),
  corner_radius: length.optional()
});
expectTypesMatch(true);
var pcb_cutout_circle = pcb_cutout_base.extend({
  shape: literalType("circle"),
  center: point,
  radius: length
});
expectTypesMatch(true);
var pcb_cutout_polygon = pcb_cutout_base.extend({
  shape: literalType("polygon"),
  points: arrayType(point)
});
expectTypesMatch(true);
var pcb_cutout_path = pcb_cutout_base.extend({
  shape: literalType("path"),
  route: arrayType(point),
  slot_width: length,
  slot_length: length.optional(),
  space_between_slots: length.optional(),
  slot_corner_radius: length.optional()
});
expectTypesMatch(true);
var pcb_cutout = discriminatedUnionType("shape", [
  pcb_cutout_rect,
  pcb_cutout_circle,
  pcb_cutout_polygon,
  pcb_cutout_path
]).describe("Defines a cutout on the PCB, removing board material.");
expectTypesMatch(true);
var pcb_missing_footprint_error = base_circuit_json_error.extend({
  type: literalType("pcb_missing_footprint_error"),
  pcb_missing_footprint_error_id: getZodPrefixedIdWithDefault("pcb_missing_footprint_error"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  error_type: literalType("pcb_missing_footprint_error").default("pcb_missing_footprint_error"),
  source_component_id: stringType()
}).describe("Defines a missing footprint error on the PCB");
expectTypesMatch(true);
var external_footprint_load_error = base_circuit_json_error.extend({
  type: literalType("external_footprint_load_error"),
  external_footprint_load_error_id: getZodPrefixedIdWithDefault("external_footprint_load_error"),
  pcb_component_id: stringType(),
  source_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  footprinter_string: stringType().optional(),
  error_type: literalType("external_footprint_load_error").default("external_footprint_load_error")
}).describe("Defines an error when an external footprint fails to load");
expectTypesMatch(true);
var circuit_json_footprint_load_error = base_circuit_json_error.extend({
  type: literalType("circuit_json_footprint_load_error"),
  circuit_json_footprint_load_error_id: getZodPrefixedIdWithDefault("circuit_json_footprint_load_error"),
  pcb_component_id: stringType(),
  source_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  error_type: literalType("circuit_json_footprint_load_error").default("circuit_json_footprint_load_error"),
  circuit_json: arrayType(anyType()).optional()
}).describe("Defines an error when a circuit JSON footprint fails to load");
expectTypesMatch(true);
var pcb_group = objectType({
  type: literalType("pcb_group"),
  pcb_group_id: getZodPrefixedIdWithDefault("pcb_group"),
  source_group_id: stringType(),
  is_subcircuit: booleanType().optional(),
  subcircuit_id: stringType().optional(),
  width: length.optional(),
  height: length.optional(),
  center: point,
  display_offset_x: stringType().optional().describe("How to display the x offset for this group, usually corresponding with how the user specified it"),
  display_offset_y: stringType().optional().describe("How to display the y offset for this group, usually corresponding with how the user specified it"),
  outline: arrayType(point).optional(),
  anchor_position: point.optional(),
  anchor_alignment: ninePointAnchor.default("center"),
  position_mode: enumType(["packed", "relative_to_group_anchor", "none"]).optional(),
  positioned_relative_to_pcb_group_id: stringType().optional(),
  positioned_relative_to_pcb_board_id: stringType().optional(),
  pcb_component_ids: arrayType(stringType()),
  child_layout_mode: enumType(["packed", "none"]).optional(),
  name: stringType().optional(),
  description: stringType().optional(),
  layout_mode: stringType().optional(),
  autorouter_configuration: objectType({
    trace_clearance: length
  }).optional(),
  autorouter_used_string: stringType().optional()
}).describe("Defines a group of components on the PCB");
expectTypesMatch(true);
var pcb_autorouting_error = base_circuit_json_error.extend({
  type: literalType("pcb_autorouting_error"),
  pcb_error_id: getZodPrefixedIdWithDefault("pcb_autorouting_error"),
  error_type: literalType("pcb_autorouting_error").default("pcb_autorouting_error"),
  subcircuit_id: stringType().optional()
}).describe("The autorouting has failed to route a portion of the board");
expectTypesMatch(true);
var pcb_preflight_routing_error = base_circuit_json_error.extend({
  type: literalType("pcb_preflight_routing_error"),
  pcb_preflight_routing_error_id: getZodPrefixedIdWithDefault("pcb_preflight_routing_error"),
  error_type: literalType("pcb_preflight_routing_error").default("pcb_preflight_routing_error"),
  error_code: stringType(),
  subcircuit_id: stringType().optional(),
  pcb_group_id: stringType().optional(),
  routing_phase_index: numberType().int().optional(),
  phase_name: stringType().optional(),
  source_trace_ids: arrayType(stringType()).optional(),
  pcb_component_ids: arrayType(stringType()).optional(),
  pcb_port_ids: arrayType(stringType()).optional(),
  related_error_ids: arrayType(stringType()).optional(),
  measurements: recordType(numberType().finite()).optional()
});
expectTypesMatch(true);
var pcb_manual_edit_conflict_warning = objectType({
  type: literalType("pcb_manual_edit_conflict_warning"),
  pcb_manual_edit_conflict_warning_id: getZodPrefixedIdWithDefault("pcb_manual_edit_conflict_warning"),
  warning_type: literalType("pcb_manual_edit_conflict_warning").default("pcb_manual_edit_conflict_warning"),
  message: stringType(),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  source_component_id: stringType()
}).describe("Warning emitted when a component has both manual placement and explicit pcbX/pcbY coordinates");
expectTypesMatch(true);
var connectorOrientationDirection = enumType(["x-", "x+", "y+", "y-"]);
var pcb_connector_not_in_accessible_orientation_warning = objectType({
  type: literalType("pcb_connector_not_in_accessible_orientation_warning"),
  pcb_connector_not_in_accessible_orientation_warning_id: getZodPrefixedIdWithDefault("pcb_connector_not_in_accessible_orientation_warning"),
  warning_type: literalType("pcb_connector_not_in_accessible_orientation_warning").default("pcb_connector_not_in_accessible_orientation_warning"),
  message: stringType(),
  pcb_component_id: stringType(),
  source_component_id: stringType().optional(),
  pcb_board_id: stringType().optional(),
  facing_direction: connectorOrientationDirection,
  recommended_facing_direction: connectorOrientationDirection,
  subcircuit_id: stringType().optional()
}).describe("Warning emitted when a connector PCB component is facing inward toward the board and should be reoriented to an outward-facing direction");
expectTypesMatch(true);
var pcb_component_missing_courtyard_warning = objectType({
  type: literalType("pcb_component_missing_courtyard_warning"),
  pcb_component_missing_courtyard_warning_id: getZodPrefixedIdWithDefault("pcb_component_missing_courtyard_warning"),
  warning_type: literalType("pcb_component_missing_courtyard_warning").default("pcb_component_missing_courtyard_warning"),
  message: stringType(),
  pcb_component_id: stringType(),
  source_component_id: stringType().optional(),
  subcircuit_id: stringType().optional()
}).describe("Warning emitted when a PCB component has no courtyard geometry");
expectTypesMatch(true);
var supplier_footprint_mismatch_warning = objectType({
  type: literalType("supplier_footprint_mismatch_warning"),
  supplier_footprint_mismatch_warning_id: getZodPrefixedIdWithDefault("supplier_footprint_mismatch_warning"),
  warning_type: literalType("supplier_footprint_mismatch_warning").default("supplier_footprint_mismatch_warning"),
  message: stringType(),
  source_component_id: stringType(),
  pcb_component_id: stringType().optional(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  supplier_name: supplier_name.optional(),
  supplier_part_number: stringType().optional(),
  supplier_footprint_url: stringType().optional(),
  footprint_copper_intersection_over_union: numberType()
}).describe("Warning emitted when a supplier part footprint does not match the expected footprint");
expectTypesMatch(true);
var pcb_fabricator_extra_charge_warning = objectType({
  type: literalType("pcb_fabricator_extra_charge_warning"),
  pcb_fabricator_extra_charge_warning_id: getZodPrefixedIdWithDefault("pcb_fabricator_extra_charge_warning"),
  warning_type: literalType("pcb_fabricator_extra_charge_warning").default("pcb_fabricator_extra_charge_warning"),
  message: stringType(),
  fabricator_preset: stringType(),
  pcb_board_id: stringType().optional(),
  pcb_via_ids: arrayType(stringType()).optional(),
  subcircuit_id: stringType().optional()
}).describe("Warning that a design feature incurs an extra charge for the selected fabricator preset, such as via hole diameters below 0.3 mm with JLCPCB economy or standard presets.");
expectTypesMatch(true);
var pcb_breakout_point = objectType({
  type: literalType("pcb_breakout_point"),
  pcb_breakout_point_id: getZodPrefixedIdWithDefault("pcb_breakout_point"),
  pcb_group_id: stringType(),
  subcircuit_id: stringType().optional(),
  source_trace_id: stringType().optional(),
  source_port_id: stringType().optional(),
  source_net_id: stringType().optional(),
  layer: layer_ref.optional(),
  x: distance,
  y: distance
}).describe("Defines a routing target within a pcb_group for a source_trace or source_net");
expectTypesMatch(true);
var pcb_ground_plane = objectType({
  type: literalType("pcb_ground_plane"),
  pcb_ground_plane_id: getZodPrefixedIdWithDefault("pcb_ground_plane"),
  source_pcb_ground_plane_id: stringType(),
  source_net_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional()
}).describe("Defines a ground plane on the PCB");
expectTypesMatch(true);
var pcb_ground_plane_region = objectType({
  type: literalType("pcb_ground_plane_region"),
  pcb_ground_plane_region_id: getZodPrefixedIdWithDefault("pcb_ground_plane_region"),
  pcb_ground_plane_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  layer: layer_ref,
  points: arrayType(point)
}).describe("Defines a polygon region of a ground plane");
expectTypesMatch(true);
var pcb_thermal_spoke = objectType({
  type: literalType("pcb_thermal_spoke"),
  pcb_thermal_spoke_id: getZodPrefixedIdWithDefault("pcb_thermal_spoke"),
  pcb_ground_plane_id: stringType(),
  shape: stringType(),
  spoke_count: numberType(),
  spoke_thickness: distance,
  spoke_inner_diameter: distance,
  spoke_outer_diameter: distance,
  pcb_plated_hole_id: stringType().optional(),
  subcircuit_id: stringType().optional()
}).describe("Pattern for connecting a ground plane to a plated hole");
expectTypesMatch(true);
var pcb_copper_pour_base = objectType({
  type: literalType("pcb_copper_pour"),
  pcb_copper_pour_id: getZodPrefixedIdWithDefault("pcb_copper_pour"),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  layer: layer_ref,
  source_net_id: stringType().optional(),
  covered_with_solder_mask: booleanType().optional().default(true)
});
var pcb_copper_pour_rect = pcb_copper_pour_base.extend({
  shape: literalType("rect"),
  center: point,
  width: length,
  height: length,
  rotation: rotation.optional()
});
expectTypesMatch(true);
var pcb_copper_pour_brep = pcb_copper_pour_base.extend({
  shape: literalType("brep"),
  brep_shape
});
expectTypesMatch(true);
var pcb_copper_pour_polygon = pcb_copper_pour_base.extend({
  shape: literalType("polygon"),
  points: arrayType(point)
});
expectTypesMatch(true);
var pcb_copper_pour = discriminatedUnionType("shape", [
  pcb_copper_pour_rect,
  pcb_copper_pour_brep,
  pcb_copper_pour_polygon
]).describe("Defines a copper pour on the PCB.");
expectTypesMatch(true);
var pcb_component_outside_board_error = base_circuit_json_error.extend({
  type: literalType("pcb_component_outside_board_error"),
  pcb_component_outside_board_error_id: getZodPrefixedIdWithDefault("pcb_component_outside_board_error"),
  error_type: literalType("pcb_component_outside_board_error").default("pcb_component_outside_board_error"),
  pcb_component_id: stringType(),
  pcb_board_id: stringType(),
  component_center: point,
  component_bounds: objectType({
    min_x: numberType(),
    max_x: numberType(),
    min_y: numberType(),
    max_y: numberType()
  }),
  subcircuit_id: stringType().optional(),
  source_component_id: stringType().optional()
}).describe("Error emitted when a PCB component is placed outside the board boundaries");
expectTypesMatch(true);
var pcb_component_not_on_board_edge_error = base_circuit_json_error.extend({
  type: literalType("pcb_component_not_on_board_edge_error"),
  pcb_component_not_on_board_edge_error_id: getZodPrefixedIdWithDefault("pcb_component_not_on_board_edge_error"),
  error_type: literalType("pcb_component_not_on_board_edge_error").default("pcb_component_not_on_board_edge_error"),
  pcb_component_id: stringType(),
  pcb_board_id: stringType(),
  component_center: point,
  pad_to_nearest_board_edge_distance: numberType(),
  source_component_id: stringType().optional(),
  subcircuit_id: stringType().optional()
}).describe("Error emitted when a component that must be placed on the board edge is centered away from the edge");
expectTypesMatch(true);
var pcb_component_invalid_layer_error = base_circuit_json_error.extend({
  type: literalType("pcb_component_invalid_layer_error"),
  pcb_component_invalid_layer_error_id: getZodPrefixedIdWithDefault("pcb_component_invalid_layer_error"),
  error_type: literalType("pcb_component_invalid_layer_error").default("pcb_component_invalid_layer_error"),
  pcb_component_id: stringType().optional(),
  source_component_id: stringType(),
  layer: layer_ref,
  subcircuit_id: stringType().optional()
}).describe("Error emitted when a component is placed on an invalid layer (components can only be on 'top' or 'bottom' layers)");
expectTypesMatch(true);
var pcb_via_clearance_error = base_circuit_json_error.extend({
  type: literalType("pcb_via_clearance_error"),
  pcb_error_id: getZodPrefixedIdWithDefault("pcb_error"),
  error_type: literalType("pcb_via_clearance_error").default("pcb_via_clearance_error"),
  pcb_via_ids: arrayType(stringType()).min(2),
  minimum_clearance: distance.optional(),
  actual_clearance: distance.optional(),
  pcb_center: objectType({
    x: numberType().optional(),
    y: numberType().optional()
  }).optional(),
  subcircuit_id: stringType().optional()
}).describe("Error emitted when vias are closer than the allowed clearance");
expectTypesMatch(true);
var pcb_via_trace_clearance_error = base_circuit_json_error.extend({
  type: literalType("pcb_via_trace_clearance_error"),
  pcb_via_trace_clearance_error_id: getZodPrefixedIdWithDefault("pcb_via_trace_clearance_error"),
  error_type: literalType("pcb_via_trace_clearance_error").default("pcb_via_trace_clearance_error"),
  pcb_via_id: stringType(),
  pcb_trace_id: stringType(),
  minimum_clearance: distance.optional(),
  actual_clearance: distance.optional(),
  center: objectType({
    x: numberType().optional(),
    y: numberType().optional()
  }).optional(),
  subcircuit_id: stringType().optional()
}).describe("Error emitted when a via and trace are closer than the allowed clearance");
expectTypesMatch(true);
var pcb_pad_pad_clearance_error = base_circuit_json_error.extend({
  type: literalType("pcb_pad_pad_clearance_error"),
  pcb_pad_pad_clearance_error_id: getZodPrefixedIdWithDefault("pcb_pad_pad_clearance_error"),
  error_type: literalType("pcb_pad_pad_clearance_error").default("pcb_pad_pad_clearance_error"),
  pcb_pad_ids: arrayType(stringType()).min(2),
  minimum_clearance: distance.optional(),
  actual_clearance: distance.optional(),
  center: objectType({
    x: numberType().optional(),
    y: numberType().optional()
  }).optional(),
  subcircuit_id: stringType().optional()
}).describe("Error emitted when pads are closer than the allowed clearance");
expectTypesMatch(true);
var pcb_pad_trace_clearance_error = base_circuit_json_error.extend({
  type: literalType("pcb_pad_trace_clearance_error"),
  pcb_pad_trace_clearance_error_id: getZodPrefixedIdWithDefault("pcb_pad_trace_clearance_error"),
  error_type: literalType("pcb_pad_trace_clearance_error").default("pcb_pad_trace_clearance_error"),
  pcb_pad_id: stringType(),
  pcb_trace_id: stringType(),
  minimum_clearance: distance.optional(),
  actual_clearance: distance.optional(),
  center: objectType({
    x: numberType().optional(),
    y: numberType().optional()
  }).optional(),
  subcircuit_id: stringType().optional()
}).describe("Error emitted when a pad and trace are closer than allowed clearance");
expectTypesMatch(true);
var pcb_courtyard_rect = objectType({
  type: literalType("pcb_courtyard_rect"),
  pcb_courtyard_rect_id: getZodPrefixedIdWithDefault("pcb_courtyard_rect"),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  center: point,
  width: length,
  height: length,
  layer: visible_layer,
  ccw_rotation: rotation.optional(),
  color: stringType().optional()
}).describe("Defines a courtyard rectangle on the PCB");
expectTypesMatch(true);
var pcb_courtyard_outline = objectType({
  type: literalType("pcb_courtyard_outline"),
  pcb_courtyard_outline_id: getZodPrefixedIdWithDefault("pcb_courtyard_outline"),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  layer: visible_layer,
  outline: arrayType(point).min(2)
}).describe("Defines a courtyard outline on the PCB");
expectTypesMatch(true);
var pcb_courtyard_polygon = objectType({
  type: literalType("pcb_courtyard_polygon"),
  pcb_courtyard_polygon_id: getZodPrefixedIdWithDefault("pcb_courtyard_polygon"),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  layer: visible_layer,
  points: arrayType(point).min(3),
  color: stringType().optional()
}).describe("Defines a courtyard polygon on the PCB");
expectTypesMatch(true);
var pcb_courtyard_circle = objectType({
  type: literalType("pcb_courtyard_circle"),
  pcb_courtyard_circle_id: getZodPrefixedIdWithDefault("pcb_courtyard_circle"),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  center: point,
  radius: length,
  layer: visible_layer,
  color: stringType().optional()
}).describe("Defines a courtyard circle on the PCB");
expectTypesMatch(true);
var pcb_courtyard_pill = objectType({
  type: literalType("pcb_courtyard_pill"),
  pcb_courtyard_pill_id: getZodPrefixedIdWithDefault("pcb_courtyard_pill"),
  pcb_component_id: stringType(),
  pcb_group_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  center: point,
  width: length,
  height: length,
  radius: length,
  layer: visible_layer,
  color: stringType().optional()
}).describe("Defines a courtyard pill on the PCB");
expectTypesMatch(true);
var cad_model_formats = [
  "obj",
  "stl",
  "3mf",
  "gltf",
  "glb",
  "step",
  "wrl"
];
var cad_model_axis_directions = [
  "x+",
  "x-",
  "y+",
  "y-",
  "z+",
  "z-"
];
var cadModelDefaultDirectionMap = {
  obj: "z+",
  stl: "z+",
  "3mf": "z+",
  gltf: "y+",
  glb: "y+",
  step: "z+",
  wrl: "y+"
};
var cad_component = objectType({
  type: literalType("cad_component"),
  cad_component_id: stringType(),
  pcb_component_id: stringType().optional().describe("Optional PCB component reference; omit for CAD geometry without a PCB component"),
  source_component_id: stringType(),
  position: point3,
  rotation: point3.optional(),
  is_on_folded_board: booleanType().optional().describe("True when position and rotation describe the assembled folded board pose. False or omitted means the flat board pose. PCB records remain flat; pcb_component_id identifies the flat mount and owning board for reversible transforms."),
  size: point3.optional(),
  layer: layer_ref.optional(),
  subcircuit_id: stringType().optional(),
  footprinter_string: stringType().optional(),
  model_obj_url: stringType().optional(),
  model_stl_url: stringType().optional(),
  model_3mf_url: stringType().optional(),
  model_gltf_url: stringType().optional(),
  model_glb_url: stringType().optional(),
  model_step_url: stringType().optional(),
  model_wrl_url: stringType().optional(),
  model_asset: asset.optional(),
  model_unit_to_mm_scale_factor: numberType().optional(),
  model_board_normal_direction: enumType(cad_model_axis_directions).optional().describe(`The direction in the model's coordinate space that is considered "up" or "coming out of the board surface"`),
  model_origin_position: point3.optional(),
  model_origin_alignment: enumType([
    "unknown",
    "center",
    "center_of_component_on_board_surface",
    "bottom_center_of_component"
  ]).optional(),
  model_object_fit: enumType(["contain_within_bounds", "fill_bounds"]).optional().default("contain_within_bounds"),
  model_jscad: anyType().optional(),
  show_as_translucent_model: booleanType().optional(),
  show_as_bounding_box: booleanType().optional(),
  show_hidden_edges: booleanType().optional(),
  anchor_alignment: enumType(["center", "center_of_component_on_board_surface"]).optional().default("center")
}).describe("Defines CAD geometry, optionally associated with a PCB component");
expectTypesMatch(true);
var wave_shape = enumType(["sinewave", "square", "triangle", "sawtooth"]);
var percentage = unionType([stringType(), numberType()]).transform((val) => {
  if (typeof val === "string") {
    if (val.endsWith("%")) {
      return parseFloat(val.slice(0, -1)) / 100;
    }
    return parseFloat(val);
  }
  return val;
}).pipe(numberType().min(0, "Duty cycle must be non-negative").max(1, "Duty cycle cannot be greater than 100%"));
var simulation_dc_voltage_source = objectType({
  type: literalType("simulation_voltage_source"),
  simulation_voltage_source_id: getZodPrefixedIdWithDefault("simulation_voltage_source"),
  is_dc_source: literalType(true).optional().default(true),
  positive_source_port_id: stringType().optional(),
  negative_source_port_id: stringType().optional(),
  positive_source_net_id: stringType().optional(),
  negative_source_net_id: stringType().optional(),
  voltage,
  ac_magnitude: voltage.optional(),
  ac_phase: rotation.optional()
}).describe("Defines a DC voltage source for simulation");
var simulation_ac_voltage_source = objectType({
  type: literalType("simulation_voltage_source"),
  simulation_voltage_source_id: getZodPrefixedIdWithDefault("simulation_voltage_source"),
  is_dc_source: literalType(false),
  terminal1_source_port_id: stringType().optional(),
  terminal2_source_port_id: stringType().optional(),
  terminal1_source_net_id: stringType().optional(),
  terminal2_source_net_id: stringType().optional(),
  voltage: voltage.optional(),
  frequency: frequency.optional(),
  peak_to_peak_voltage: voltage.optional(),
  wave_shape: wave_shape.optional(),
  phase: rotation.optional(),
  duty_cycle: percentage.optional(),
  pulse_delay: ms.optional(),
  rise_time: ms.optional(),
  fall_time: ms.optional(),
  pulse_width: ms.optional(),
  period: ms.optional(),
  ac_magnitude: voltage.optional(),
  ac_phase: rotation.optional()
}).describe("Defines an AC voltage source for simulation");
var simulation_voltage_source = unionType([simulation_dc_voltage_source, simulation_ac_voltage_source]).describe("Defines a voltage source for simulation");
expectTypesMatch(true);
expectTypesMatch(true);
expectTypesMatch(true);
var percentage2 = unionType([stringType(), numberType()]).transform((val) => {
  if (typeof val === "string") {
    if (val.endsWith("%")) {
      return parseFloat(val.slice(0, -1)) / 100;
    }
    return parseFloat(val);
  }
  return val;
}).pipe(numberType().min(0, "Duty cycle must be non-negative").max(1, "Duty cycle cannot be greater than 100%"));
var simulation_dc_current_source = objectType({
  type: literalType("simulation_current_source"),
  simulation_current_source_id: getZodPrefixedIdWithDefault("simulation_current_source"),
  is_dc_source: literalType(true).optional().default(true),
  positive_source_port_id: stringType().optional(),
  negative_source_port_id: stringType().optional(),
  positive_source_net_id: stringType().optional(),
  negative_source_net_id: stringType().optional(),
  current,
  ac_magnitude: current.optional(),
  ac_phase: rotation.optional()
}).describe("Defines a DC current source for simulation");
var simulation_ac_current_source = objectType({
  type: literalType("simulation_current_source"),
  simulation_current_source_id: getZodPrefixedIdWithDefault("simulation_current_source"),
  is_dc_source: literalType(false),
  terminal1_source_port_id: stringType().optional(),
  terminal2_source_port_id: stringType().optional(),
  terminal1_source_net_id: stringType().optional(),
  terminal2_source_net_id: stringType().optional(),
  current: current.optional(),
  frequency: frequency.optional(),
  peak_to_peak_current: current.optional(),
  wave_shape: wave_shape.optional(),
  phase: rotation.optional(),
  duty_cycle: percentage2.optional(),
  ac_magnitude: current.optional(),
  ac_phase: rotation.optional()
}).describe("Defines an AC current source for simulation");
var simulation_current_source = unionType([simulation_dc_current_source, simulation_ac_current_source]).describe("Defines a current source for simulation");
expectTypesMatch(true);
expectTypesMatch(true);
expectTypesMatch(true);
var simulation_dc_sweep_unit = custom((dcSweepUnit) => dcSweepUnit === "V" || dcSweepUnit === "A");
var simulation_parameter_unit = custom((parameterUnit) => parameterUnit === "Ω" || parameterUnit === "F" || parameterUnit === "H" || parameterUnit === "V" || parameterUnit === "A");
var experiment_type = unionType([
  literalType("spice_dc_sweep"),
  literalType("spice_dc_operating_point"),
  literalType("spice_transient_analysis"),
  literalType("spice_ac_analysis")
]);
var spice_simulation_options = objectType({
  method: enumType(["trap", "gear"]).optional(),
  reltol: unionType([numberType(), stringType()]).optional(),
  abstol: unionType([numberType(), stringType()]).optional(),
  vntol: unionType([numberType(), stringType()]).optional()
}).describe("SPICE solver options for a simulation experiment");
var simulation_experiment = objectType({
  type: literalType("simulation_experiment"),
  simulation_experiment_id: getZodPrefixedIdWithDefault("simulation_experiment"),
  name: stringType(),
  experiment_type,
  time_per_step: duration_ms.optional(),
  start_time_ms: ms.optional(),
  end_time_ms: ms.optional(),
  spice_options: spice_simulation_options.optional(),
  dc_sweep_voltage_source_id: stringType().optional(),
  dc_sweep_current_source_id: stringType().optional(),
  dc_sweep_start: numberType().optional(),
  dc_sweep_stop: numberType().optional(),
  dc_sweep_step: numberType().refine((dcSweepStep) => dcSweepStep !== 0).optional(),
  dc_sweep_unit: simulation_dc_sweep_unit.optional(),
  ac_sweep_type: enumType(["linear", "decade", "octave"]).optional(),
  ac_samples_per_interval: numberType().int().positive().optional(),
  ac_sample_count: numberType().int().positive().optional(),
  ac_start_frequency_hz: numberType().positive().optional(),
  ac_stop_frequency_hz: numberType().positive().optional()
}).superRefine((experiment, context) => {
  if (experiment.experiment_type === "spice_dc_sweep") {
    const requiredFields = [
      "dc_sweep_start",
      "dc_sweep_stop",
      "dc_sweep_step",
      "dc_sweep_unit"
    ];
    for (const field of requiredFields) {
      if (experiment[field] === undefined) {
        context.addIssue({
          code: ZodIssueCode.custom,
          path: [field],
          message: `${field} is required for a DC sweep`
        });
      }
    }
    const hasVoltageSource = experiment.dc_sweep_voltage_source_id !== undefined;
    const hasCurrentSource = experiment.dc_sweep_current_source_id !== undefined;
    if (hasVoltageSource === hasCurrentSource) {
      context.addIssue({
        code: ZodIssueCode.custom,
        path: ["dc_sweep_voltage_source_id"],
        message: "Exactly one DC sweep voltage or current source ID is required"
      });
    }
  }
  if (experiment.experiment_type === "spice_ac_analysis") {
    if (experiment.ac_sweep_type === undefined) {
      context.addIssue({
        code: ZodIssueCode.custom,
        path: ["ac_sweep_type"],
        message: "ac_sweep_type is required for an AC analysis"
      });
    }
    if (experiment.ac_start_frequency_hz === undefined) {
      context.addIssue({
        code: ZodIssueCode.custom,
        path: ["ac_start_frequency_hz"],
        message: "ac_start_frequency_hz is required for an AC analysis"
      });
    }
    if (experiment.ac_stop_frequency_hz === undefined) {
      context.addIssue({
        code: ZodIssueCode.custom,
        path: ["ac_stop_frequency_hz"],
        message: "ac_stop_frequency_hz is required for an AC analysis"
      });
    }
    if (experiment.ac_sweep_type === "linear" && experiment.ac_sample_count === undefined) {
      context.addIssue({
        code: ZodIssueCode.custom,
        path: ["ac_sample_count"],
        message: "ac_sample_count is required for a linear AC analysis"
      });
    }
    if ((experiment.ac_sweep_type === "decade" || experiment.ac_sweep_type === "octave") && experiment.ac_samples_per_interval === undefined) {
      context.addIssue({
        code: ZodIssueCode.custom,
        path: ["ac_samples_per_interval"],
        message: "ac_samples_per_interval is required for decade and octave AC analyses"
      });
    }
  }
}).describe("Defines a simulation experiment configuration");
expectTypesMatch(true);
var simulation_parameter_sweep_coordinate = objectType({
  simulation_parameter_sweep_id: stringType(),
  sweep_index: numberType().int().nonnegative(),
  parameter_value: numberType(),
  parameter_unit: simulation_parameter_unit
});
expectTypesMatch(true);
var simulation_transient_voltage_graph = objectType({
  type: literalType("simulation_transient_voltage_graph"),
  simulation_transient_voltage_graph_id: getZodPrefixedIdWithDefault("simulation_transient_voltage_graph"),
  simulation_experiment_id: stringType(),
  simulation_parameter_sweep_coordinate: simulation_parameter_sweep_coordinate.optional(),
  timestamps_ms: arrayType(numberType()).optional(),
  voltage_levels: arrayType(numberType()),
  source_component_id: stringType().optional(),
  subcircuit_connectivity_map_key: stringType().optional(),
  time_per_step: duration_ms,
  start_time_ms: ms,
  end_time_ms: ms,
  name: stringType().optional(),
  color: stringType().optional()
}).describe("Stores voltage measurements over time for a simulation");
expectTypesMatch(true);
var simulation_transient_current_graph = objectType({
  type: literalType("simulation_transient_current_graph"),
  simulation_transient_current_graph_id: getZodPrefixedIdWithDefault("simulation_transient_current_graph"),
  simulation_experiment_id: stringType(),
  simulation_parameter_sweep_coordinate: simulation_parameter_sweep_coordinate.optional(),
  timestamps_ms: arrayType(numberType()).optional(),
  current_levels: arrayType(numberType()),
  source_component_id: stringType().optional(),
  subcircuit_connectivity_map_key: stringType().optional(),
  time_per_step: duration_ms,
  start_time_ms: ms,
  end_time_ms: ms,
  name: stringType().optional(),
  color: stringType().optional()
}).describe("Stores current measurements over time for a simulation");
expectTypesMatch(true);
var simulation_switch = objectType({
  type: literalType("simulation_switch"),
  simulation_switch_id: getZodPrefixedIdWithDefault("simulation_switch"),
  source_component_id: stringType().optional(),
  closes_at: ms.optional(),
  opens_at: ms.optional(),
  starts_closed: booleanType().optional(),
  switching_frequency: frequency.optional()
}).describe("Defines a switch for simulation timing control");
expectTypesMatch(true);
var simulation_voltage_probe = objectType({
  type: literalType("simulation_voltage_probe"),
  simulation_voltage_probe_id: getZodPrefixedIdWithDefault("simulation_voltage_probe"),
  source_component_id: stringType().optional(),
  name: stringType().optional(),
  signal_input_source_port_id: stringType().optional(),
  signal_input_source_net_id: stringType().optional(),
  reference_input_source_port_id: stringType().optional(),
  reference_input_source_net_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  color: stringType().optional()
}).describe("Defines a voltage probe for simulation. If a reference input is not provided, it measures against ground. If a reference input is provided, it measures the differential voltage between two points.").superRefine((data, ctx) => {
  const is_differential = data.reference_input_source_port_id || data.reference_input_source_net_id;
  if (is_differential) {
    const has_ports = !!data.signal_input_source_port_id || !!data.reference_input_source_port_id;
    const has_nets = !!data.signal_input_source_net_id || !!data.reference_input_source_net_id;
    if (has_ports && has_nets) {
      ctx.addIssue({
        code: ZodIssueCode.custom,
        message: "Cannot mix port and net connections in a differential probe."
      });
    } else if (has_ports) {
      if (!data.signal_input_source_port_id || !data.reference_input_source_port_id) {
        ctx.addIssue({
          code: ZodIssueCode.custom,
          message: "Differential port probe requires both signal_input_source_port_id and reference_input_source_port_id."
        });
      }
    } else if (has_nets) {
      if (!data.signal_input_source_net_id || !data.reference_input_source_net_id) {
        ctx.addIssue({
          code: ZodIssueCode.custom,
          message: "Differential net probe requires both signal_input_source_net_id and reference_input_source_net_id."
        });
      }
    }
  } else {
    if (!!data.signal_input_source_port_id === !!data.signal_input_source_net_id) {
      ctx.addIssue({
        code: ZodIssueCode.custom,
        message: "A voltage probe must have exactly one of signal_input_source_port_id or signal_input_source_net_id."
      });
    }
  }
});
expectTypesMatch(true);
var simulation_current_probe = objectType({
  type: literalType("simulation_current_probe"),
  simulation_current_probe_id: getZodPrefixedIdWithDefault("simulation_current_probe"),
  source_component_id: stringType().optional(),
  name: stringType().optional(),
  positive_source_port_id: stringType().optional(),
  negative_source_port_id: stringType().optional(),
  positive_source_net_id: stringType().optional(),
  negative_source_net_id: stringType().optional(),
  subcircuit_id: stringType().optional(),
  color: stringType().optional()
}).describe("Defines a current probe for simulation. It measures current flowing from the positive endpoint to the negative endpoint.").superRefine((data, ctx) => {
  const hasPositivePort = !!data.positive_source_port_id;
  const hasNegativePort = !!data.negative_source_port_id;
  const hasPositiveNet = !!data.positive_source_net_id;
  const hasNegativeNet = !!data.negative_source_net_id;
  const hasPorts = hasPositivePort || hasNegativePort;
  const hasNets = hasPositiveNet || hasNegativeNet;
  if (hasPorts && hasNets) {
    ctx.addIssue({
      code: ZodIssueCode.custom,
      message: "Cannot mix port and net connections in a current probe."
    });
    return;
  }
  if (hasPorts) {
    if (!hasPositivePort || !hasNegativePort) {
      ctx.addIssue({
        code: ZodIssueCode.custom,
        message: "Current probe using source ports requires both positive_source_port_id and negative_source_port_id."
      });
    }
    return;
  }
  if (hasNets) {
    if (!hasPositiveNet || !hasNegativeNet) {
      ctx.addIssue({
        code: ZodIssueCode.custom,
        message: "Current probe using source nets requires both positive_source_net_id and negative_source_net_id."
      });
    }
    return;
  }
  ctx.addIssue({
    code: ZodIssueCode.custom,
    message: "A current probe must have either positive/negative source port ids or positive/negative source net ids."
  });
});
expectTypesMatch(true);
var simulation_unknown_experiment_error = base_circuit_json_error.extend({
  type: literalType("simulation_unknown_experiment_error"),
  simulation_unknown_experiment_error_id: getZodPrefixedIdWithDefault("simulation_unknown_experiment_error"),
  error_type: literalType("simulation_unknown_experiment_error").default("simulation_unknown_experiment_error"),
  simulation_experiment_id: stringType().optional(),
  subcircuit_id: stringType().optional()
}).describe("An unknown error occurred during the simulation experiment.");
expectTypesMatch(true);
var simulation_parameter_type = enumType([
  "resistance",
  "capacitance",
  "inductance",
  "voltage",
  "current"
]);
var simulation_parameter_sweep_base = objectType({
  type: literalType("simulation_parameter_sweep"),
  simulation_parameter_sweep_id: getZodPrefixedIdWithDefault("simulation_parameter_sweep"),
  simulation_experiment_id: stringType(),
  name: stringType().optional(),
  parameter_values: arrayType(numberType()).min(1),
  parameter_unit: simulation_parameter_unit
});
var simulation_parameter_sweep = discriminatedUnionType("parameter_type", [
  simulation_parameter_sweep_base.extend({
    parameter_type: literalType("resistance"),
    resistor_source_component_id: stringType()
  }),
  simulation_parameter_sweep_base.extend({
    parameter_type: literalType("capacitance"),
    capacitor_source_component_id: stringType()
  }),
  simulation_parameter_sweep_base.extend({
    parameter_type: literalType("inductance"),
    inductor_source_component_id: stringType()
  }),
  simulation_parameter_sweep_base.extend({
    parameter_type: literalType("voltage"),
    source_net_id: stringType()
  }),
  simulation_parameter_sweep_base.extend({
    parameter_type: literalType("current"),
    current_source_component_id: stringType()
  })
]).describe("Repeats a simulation experiment over component parameter values");
expectTypesMatch(true);
var simulation_dc_operating_point_voltage = objectType({
  type: literalType("simulation_dc_operating_point_voltage"),
  simulation_dc_operating_point_voltage_id: getZodPrefixedIdWithDefault("simulation_dc_operating_point_voltage"),
  simulation_experiment_id: stringType(),
  simulation_parameter_sweep_coordinate: simulation_parameter_sweep_coordinate.optional(),
  simulation_voltage_probe_id: stringType(),
  voltage: numberType(),
  name: stringType().optional(),
  color: stringType().optional()
});
expectTypesMatch(true);
var simulation_dc_operating_point_current = objectType({
  type: literalType("simulation_dc_operating_point_current"),
  simulation_dc_operating_point_current_id: getZodPrefixedIdWithDefault("simulation_dc_operating_point_current"),
  simulation_experiment_id: stringType(),
  simulation_parameter_sweep_coordinate: simulation_parameter_sweep_coordinate.optional(),
  simulation_current_probe_id: stringType(),
  current: numberType(),
  name: stringType().optional(),
  color: stringType().optional()
});
expectTypesMatch(true);
var simulation_dc_sweep_voltage_graph = objectType({
  type: literalType("simulation_dc_sweep_voltage_graph"),
  simulation_dc_sweep_voltage_graph_id: getZodPrefixedIdWithDefault("simulation_dc_sweep_voltage_graph"),
  simulation_experiment_id: stringType(),
  simulation_parameter_sweep_coordinate: simulation_parameter_sweep_coordinate.optional(),
  simulation_voltage_probe_id: stringType(),
  sweep_values: arrayType(numberType()),
  sweep_unit: simulation_dc_sweep_unit,
  voltage_levels: arrayType(numberType()),
  name: stringType().optional(),
  color: stringType().optional()
}).refine((graph) => graph.sweep_values.length === graph.voltage_levels.length, {
  message: "sweep_values and voltage_levels must have the same length"
});
expectTypesMatch(true);
var simulation_dc_sweep_current_graph = objectType({
  type: literalType("simulation_dc_sweep_current_graph"),
  simulation_dc_sweep_current_graph_id: getZodPrefixedIdWithDefault("simulation_dc_sweep_current_graph"),
  simulation_experiment_id: stringType(),
  simulation_parameter_sweep_coordinate: simulation_parameter_sweep_coordinate.optional(),
  simulation_current_probe_id: stringType(),
  sweep_values: arrayType(numberType()),
  sweep_unit: simulation_dc_sweep_unit,
  current_levels: arrayType(numberType()),
  name: stringType().optional(),
  color: stringType().optional()
}).refine((graph) => graph.sweep_values.length === graph.current_levels.length, {
  message: "sweep_values and current_levels must have the same length"
});
expectTypesMatch(true);
var simulation_complex_sample = objectType({
  re: numberType(),
  im: numberType()
});
expectTypesMatch(true);
var simulation_ac_sweep_voltage_graph = objectType({
  type: literalType("simulation_ac_sweep_voltage_graph"),
  simulation_ac_sweep_voltage_graph_id: getZodPrefixedIdWithDefault("simulation_ac_sweep_voltage_graph"),
  simulation_experiment_id: stringType(),
  simulation_parameter_sweep_coordinate: simulation_parameter_sweep_coordinate.optional(),
  simulation_voltage_probe_id: stringType(),
  frequencies_hz: arrayType(numberType()),
  complex_voltages: arrayType(simulation_complex_sample),
  name: stringType().optional(),
  color: stringType().optional()
}).refine((graph) => graph.frequencies_hz.length === graph.complex_voltages.length, {
  message: "frequencies_hz and complex_voltages must have the same length"
});
expectTypesMatch(true);
var simulation_ac_sweep_current_graph = objectType({
  type: literalType("simulation_ac_sweep_current_graph"),
  simulation_ac_sweep_current_graph_id: getZodPrefixedIdWithDefault("simulation_ac_sweep_current_graph"),
  simulation_experiment_id: stringType(),
  simulation_parameter_sweep_coordinate: simulation_parameter_sweep_coordinate.optional(),
  simulation_current_probe_id: stringType(),
  frequencies_hz: arrayType(numberType()),
  complex_currents: arrayType(simulation_complex_sample),
  name: stringType().optional(),
  color: stringType().optional()
}).refine((graph) => graph.frequencies_hz.length === graph.complex_currents.length, {
  message: "frequencies_hz and complex_currents must have the same length"
});
expectTypesMatch(true);
var simulation_op_amp = objectType({
  type: literalType("simulation_op_amp"),
  simulation_op_amp_id: getZodPrefixedIdWithDefault("simulation_op_amp"),
  source_component_id: stringType().optional(),
  inverting_input_source_port_id: stringType(),
  non_inverting_input_source_port_id: stringType(),
  output_source_port_id: stringType(),
  positive_supply_source_port_id: stringType(),
  negative_supply_source_port_id: stringType()
}).describe("Defines a simple ideal operational amplifier for simulation");
expectTypesMatch(true);
var simulation_spice_subcircuit = objectType({
  type: literalType("simulation_spice_subcircuit"),
  simulation_spice_subcircuit_id: getZodPrefixedIdWithDefault("simulation_spice_subcircuit"),
  source_component_id: stringType(),
  spice_pin_to_source_port_map: recordType(stringType(), stringType()),
  subcircuit_source: stringType()
}).describe("Defines a custom SPICE subcircuit model for simulation");
expectTypesMatch(true);
var hasValue = (value) => value !== undefined;
var simulation_oscilloscope_trace = objectType({
  type: literalType("simulation_oscilloscope_trace"),
  simulation_oscilloscope_trace_id: getZodPrefixedIdWithDefault("simulation_oscilloscope_trace"),
  simulation_transient_voltage_graph_id: stringType().optional(),
  simulation_transient_current_graph_id: stringType().optional(),
  simulation_voltage_probe_id: stringType().optional(),
  simulation_current_probe_id: stringType().optional(),
  display_name: stringType().optional(),
  color: stringType().optional(),
  display_center_value: numberType().optional(),
  display_center_offset_divs: numberType().optional(),
  volts_per_div: numberType().positive().optional(),
  amps_per_div: numberType().positive().optional()
}).describe("Defines how a simulation measurement is rendered as an oscilloscope-style trace.").superRefine((data, ctx) => {
  const voltageReferences = [
    data.simulation_transient_voltage_graph_id,
    data.simulation_voltage_probe_id
  ].filter(hasValue).length;
  const currentReferences = [
    data.simulation_transient_current_graph_id,
    data.simulation_current_probe_id
  ].filter(hasValue).length;
  if (voltageReferences + currentReferences !== 1) {
    ctx.addIssue({
      code: ZodIssueCode.custom,
      message: "An oscilloscope trace must reference exactly one voltage graph, current graph, voltage probe, or current probe."
    });
  }
  if (voltageReferences > 0 && data.amps_per_div !== undefined) {
    ctx.addIssue({
      code: ZodIssueCode.custom,
      message: "Voltage oscilloscope traces must use volts_per_div, not amps_per_div."
    });
  }
  if (currentReferences > 0 && data.volts_per_div !== undefined) {
    ctx.addIssue({
      code: ZodIssueCode.custom,
      message: "Current oscilloscope traces must use amps_per_div, not volts_per_div."
    });
  }
});
expectTypesMatch(true);
var any_circuit_element = unionType([
  source_trace,
  source_bus,
  source_port,
  source_component_internal_connection,
  any_source_component,
  source_net,
  source_group,
  source_simple_chip,
  source_simple_capacitor,
  source_simple_diode,
  source_simple_led,
  source_simple_resistor,
  source_simple_power_source,
  source_simple_battery,
  source_simple_inductor,
  source_simple_pin_header,
  source_simple_pinout,
  source_simple_resonator,
  source_simple_switch,
  source_simple_transistor,
  source_simple_test_point,
  source_simple_mosfet,
  source_simple_op_amp,
  source_simple_potentiometer,
  source_simple_push_button,
  source_pcb_ground_plane,
  source_manually_placed_via,
  source_board,
  source_project_metadata,
  source_invalid_component_property_error,
  source_trace_not_connected_error,
  source_pin_missing_trace_warning,
  source_unnamed_trace_warning,
  source_confusing_net_name_warning,
  source_missing_manufacturer_part_number_warning,
  source_refdes_convention_warning,
  source_no_power_pin_defined_warning,
  source_no_ground_pin_defined_warning,
  source_component_pins_underspecified_warning,
  source_pin_must_be_connected_error,
  unknown_error_finding_part,
  source_part_not_found_warning,
  source_i2c_misconfigured_error,
  source_component_misconfigured_error,
  source_ambiguous_port_reference,
  pcb_component,
  pcb_debug_object,
  pcb_hole,
  pcb_missing_footprint_error,
  external_footprint_load_error,
  circuit_json_footprint_load_error,
  pcb_manual_edit_conflict_warning,
  pcb_connector_not_in_accessible_orientation_warning,
  pcb_component_missing_courtyard_warning,
  supplier_footprint_mismatch_warning,
  pcb_fabricator_extra_charge_warning,
  pcb_plated_hole,
  pcb_keepout,
  pcb_keepout_overlap_warning,
  pcb_port,
  pcb_net,
  pcb_text,
  pcb_trace,
  pcb_trace_warning,
  pcb_trace_too_long_warning,
  pcb_trace_too_long_error,
  pcb_bus_length_skew_error,
  pcb_trace_too_many_vias_warning,
  pcb_via,
  pcb_smtpad,
  pcb_solder_paste,
  pcb_board,
  pcb_bend,
  pcb_stiffener,
  pcb_panel,
  pcb_group,
  pcb_trace_hint,
  pcb_silkscreen_line,
  pcb_silkscreen_path,
  pcb_silkscreen_text,
  pcb_silkscreen_pill,
  pcb_copper_text,
  pcb_silkscreen_rect,
  pcb_silkscreen_circle,
  pcb_silkscreen_oval,
  pcb_silkscreen_graphic,
  pcb_trace_error,
  pcb_trace_missing_error,
  pcb_placement_error,
  pcb_packing_error,
  pcb_panelization_placement_error,
  pcb_port_not_matched_error,
  pcb_port_not_connected_error,
  pcb_via_clearance_error,
  pcb_via_trace_clearance_error,
  pcb_pad_pad_clearance_error,
  pcb_pad_trace_clearance_error,
  pcb_fabrication_note_path,
  pcb_fabrication_note_text,
  pcb_fabrication_note_rect,
  pcb_fabrication_note_dimension,
  pcb_note_text,
  pcb_note_rect,
  pcb_note_path,
  pcb_note_line,
  pcb_note_dimension,
  pcb_autorouting_error,
  pcb_preflight_routing_error,
  pcb_footprint_overlap_error,
  pcb_courtyard_overlap_error,
  pcb_breakout_point,
  pcb_cutout,
  pcb_ground_plane,
  pcb_ground_plane_region,
  pcb_thermal_spoke,
  pcb_copper_pour,
  pcb_component_outside_board_error,
  pcb_component_not_on_board_edge_error,
  pcb_component_invalid_layer_error,
  pcb_courtyard_rect,
  pcb_courtyard_outline,
  pcb_courtyard_polygon,
  pcb_courtyard_circle,
  pcb_courtyard_pill,
  schematic_box,
  schematic_text,
  schematic_line,
  schematic_rect,
  schematic_circle,
  schematic_arc,
  schematic_component,
  schematic_symbol,
  schematic_port,
  schematic_trace,
  schematic_path,
  schematic_error,
  schematic_layout_error,
  schematic_net_label,
  schematic_debug_object,
  schematic_voltage_probe,
  schematic_manual_edit_conflict_warning,
  schematic_component_overlap_warning,
  schematic_component_styling_warning,
  schematic_missing_sheet_warning,
  schematic_element_outside_sheet_warning,
  schematic_graphic,
  schematic_group,
  schematic_sheet,
  schematic_table,
  schematic_table_cell,
  cad_component,
  simulation_voltage_source,
  simulation_current_source,
  simulation_experiment,
  simulation_transient_voltage_graph,
  simulation_transient_current_graph,
  simulation_dc_operating_point_voltage,
  simulation_dc_operating_point_current,
  simulation_dc_sweep_voltage_graph,
  simulation_dc_sweep_current_graph,
  simulation_ac_sweep_voltage_graph,
  simulation_ac_sweep_current_graph,
  simulation_parameter_sweep,
  simulation_switch,
  simulation_voltage_probe,
  simulation_current_probe,
  simulation_oscilloscope_trace,
  simulation_unknown_experiment_error,
  simulation_op_amp,
  simulation_spice_subcircuit
]);
var any_soup_element = any_circuit_element;
expectTypesMatch(true);
expectStringUnionsMatch(true);

// ../../../../tools/circuit-to-wokwi/node_modules/@tscircuit/circuit-json-util/dist/index.js
var import_transformation_matrix = __toESM(require_build_commonjs(), 1);

// ../../../../tools/circuit-to-wokwi/node_modules/parsel-js/dist/parsel.min.js
var t = new Set(["combinator", "comma"]);
var n = new Set(["not", "is", "where", "has", "matches", "-moz-any", "-webkit-any", "nth-child", "nth-last-child"]);

// ../../../../tools/circuit-to-wokwi/node_modules/@tscircuit/circuit-json-util/dist/index.js
var import_transformation_matrix2 = __toESM(require_build_commonjs(), 1);
var import_transformation_matrix3 = __toESM(require_build_commonjs(), 1);
var import_transformation_matrix4 = __toESM(require_build_commonjs(), 1);
var import_transformation_matrix5 = __toESM(require_build_commonjs(), 1);

// ../../../../tools/circuit-to-wokwi/node_modules/@flatten-js/core/dist/main.mjs
var CCW = true;
var CW = false;
var ORIENTATION = { CCW: -1, CW: 1, NOT_ORIENTABLE: 0 };
var PIx2 = 2 * Math.PI;
var INSIDE$2 = 1;
var OUTSIDE$1 = 0;
var BOUNDARY$1 = 2;
var CONTAINS = 3;
var INTERLACE = 4;
var OVERLAP_SAME$1 = 1;
var OVERLAP_OPPOSITE$1 = 2;
var NOT_VERTEX$1 = 0;
var START_VERTEX$1 = 1;
var END_VERTEX$1 = 2;
var Constants = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  BOUNDARY: BOUNDARY$1,
  CCW,
  CONTAINS,
  CW,
  END_VERTEX: END_VERTEX$1,
  INSIDE: INSIDE$2,
  INTERLACE,
  NOT_VERTEX: NOT_VERTEX$1,
  ORIENTATION,
  OUTSIDE: OUTSIDE$1,
  OVERLAP_OPPOSITE: OVERLAP_OPPOSITE$1,
  OVERLAP_SAME: OVERLAP_SAME$1,
  PIx2,
  START_VERTEX: START_VERTEX$1
});
var DP_TOL = 0.000001;
function setTolerance(tolerance) {
  DP_TOL = tolerance;
}
function getTolerance() {
  return DP_TOL;
}
var DECIMALS = 3;
function EQ_0(x) {
  return x < DP_TOL && x > -DP_TOL;
}
function EQ(x, y) {
  return x - y < DP_TOL && x - y > -DP_TOL;
}
function GT(x, y) {
  return x - y > DP_TOL;
}
function GE(x, y) {
  return x - y > -DP_TOL;
}
function LT(x, y) {
  return x - y < -DP_TOL;
}
function LE(x, y) {
  return x - y < DP_TOL;
}
var Utils$1 = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  DECIMALS,
  EQ,
  EQ_0,
  GE,
  GT,
  LE,
  LT,
  getTolerance,
  setTolerance
});
var Flatten = {
  Utils: Utils$1,
  Errors: undefined,
  Matrix: undefined,
  Planar_set: undefined,
  Point: undefined,
  Vector: undefined,
  Line: undefined,
  Circle: undefined,
  Segment: undefined,
  Arc: undefined,
  Box: undefined,
  Edge: undefined,
  Face: undefined,
  Ray: undefined,
  Ray_shooting: undefined,
  Multiline: undefined,
  Polygon: undefined,
  Distance: undefined,
  Inversion: undefined
};
for (let c in Constants) {
  Flatten[c] = Constants[c];
}
Object.defineProperty(Flatten, "DP_TOL", {
  get: function() {
    return getTolerance();
  },
  set: function(value) {
    setTolerance(value);
  }
});

class Errors {
  static get ILLEGAL_PARAMETERS() {
    return new ReferenceError("Illegal Parameters");
  }
  static get ZERO_DIVISION() {
    return new Error("Zero division");
  }
  static get UNRESOLVED_BOUNDARY_CONFLICT() {
    return new Error("Unresolved boundary conflict in boolean operation");
  }
  static get INFINITE_LOOP() {
    return new Error("Infinite loop");
  }
  static get CANNOT_COMPLETE_BOOLEAN_OPERATION() {
    return new Error("Cannot complete boolean operation");
  }
  static get CANNOT_INVOKE_ABSTRACT_METHOD() {
    return new Error("Abstract method cannot be invoked");
  }
  static get OPERATION_IS_NOT_SUPPORTED() {
    return new Error("Operation is not supported");
  }
  static get UNSUPPORTED_SHAPE_TYPE() {
    return new Error("Unsupported shape type");
  }
}
Flatten.Errors = Errors;

class LinkedList {
  constructor(first, last) {
    this.first = first;
    this.last = last || this.first;
  }
  [Symbol.iterator]() {
    let value = undefined;
    return {
      next: () => {
        value = value ? value.next : this.first;
        return { value, done: value === undefined };
      }
    };
  }
  get size() {
    let counter = 0;
    for (let edge of this) {
      counter++;
    }
    return counter;
  }
  toArray(start = undefined, end = undefined) {
    let elements = [];
    let from = start || this.first;
    let to = end || this.last;
    let element = from;
    if (element === undefined)
      return elements;
    do {
      elements.push(element);
      element = element.next;
    } while (element !== to.next);
    return elements;
  }
  append(element) {
    if (this.isEmpty()) {
      this.first = element;
    } else {
      element.prev = this.last;
      this.last.next = element;
    }
    this.last = element;
    this.last.next = undefined;
    this.first.prev = undefined;
    return this;
  }
  insert(newElement, elementBefore) {
    if (this.isEmpty()) {
      this.first = newElement;
      this.last = newElement;
    } else if (elementBefore === null || elementBefore === undefined) {
      newElement.next = this.first;
      this.first.prev = newElement;
      this.first = newElement;
    } else {
      let elementAfter = elementBefore.next;
      elementBefore.next = newElement;
      if (elementAfter)
        elementAfter.prev = newElement;
      newElement.prev = elementBefore;
      newElement.next = elementAfter;
      if (this.last === elementBefore)
        this.last = newElement;
    }
    this.last.next = undefined;
    this.first.prev = undefined;
    return this;
  }
  remove(element) {
    if (element === this.first && element === this.last) {
      this.first = undefined;
      this.last = undefined;
    } else {
      if (element.prev)
        element.prev.next = element.next;
      if (element.next)
        element.next.prev = element.prev;
      if (element === this.first) {
        this.first = element.next;
      }
      if (element === this.last) {
        this.last = element.prev;
      }
    }
    return this;
  }
  isEmpty() {
    return this.first === undefined;
  }
  static testInfiniteLoop(first) {
    let edge = first;
    let controlEdge = first;
    do {
      if (edge != first && edge === controlEdge) {
        throw Errors.INFINITE_LOOP;
      }
      edge = edge.next;
      controlEdge = controlEdge.next.next;
    } while (edge != first);
  }
}
var defaultAttributes = {
  stroke: "black"
};

class SVGAttributes {
  constructor(args = defaultAttributes) {
    for (const property in args) {
      this[property] = args[property];
    }
    this.stroke = args.stroke ?? defaultAttributes.stroke;
  }
  toAttributesString() {
    return Object.keys(this).reduce((acc, key) => acc + (this[key] !== undefined ? this.toAttrString(key, this[key]) : ""), ``);
  }
  toAttrString(key, value) {
    const SVGKey = key === "className" ? "class" : this.convertCamelToKebabCase(key);
    return value === null ? `${SVGKey} ` : `${SVGKey}="${value.toString()}" `;
  }
  convertCamelToKebabCase(str) {
    return str.match(/[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g).join("-").toLowerCase();
  }
}
function convertToString(attrs) {
  return new SVGAttributes(attrs).toAttributesString();
}
function intersectLine2Line(line1, line2) {
  let ip = [];
  let [A1, B1, C1] = line1.standard;
  let [A2, B2, C2] = line2.standard;
  let det = A1 * B2 - B1 * A2;
  let detX = C1 * B2 - B1 * C2;
  let detY = A1 * C2 - C1 * A2;
  if (!Flatten.Utils.EQ_0(det)) {
    let x, y;
    if (B1 === 0) {
      x = C1 / A1;
      y = detY / det;
    } else if (B2 === 0) {
      x = C2 / A2;
      y = detY / det;
    } else if (A1 === 0) {
      x = detX / det;
      y = C1 / B1;
    } else if (A2 === 0) {
      x = detX / det;
      y = C2 / B2;
    } else {
      x = detX / det;
      y = detY / det;
    }
    ip.push(new Flatten.Point(x, y));
  }
  return ip;
}
function intersectLine2Circle(line, circle) {
  let ip = [];
  let prj = circle.pc.projectionOn(line);
  let dist = circle.pc.distanceTo(prj)[0];
  if (Flatten.Utils.EQ(dist, circle.r)) {
    ip.push(prj);
  } else if (Flatten.Utils.LT(dist, circle.r)) {
    let delta = Math.sqrt(circle.r * circle.r - dist * dist);
    let v_trans, pt;
    v_trans = line.norm.rotate90CCW().multiply(delta);
    pt = prj.translate(v_trans);
    ip.push(pt);
    v_trans = line.norm.rotate90CW().multiply(delta);
    pt = prj.translate(v_trans);
    ip.push(pt);
  }
  return ip;
}
function intersectLine2Box(line, box) {
  let ips = [];
  for (let seg of box.toSegments()) {
    let ips_tmp = intersectSegment2Line(seg, line);
    for (let pt of ips_tmp) {
      if (!ptInIntPoints(pt, ips)) {
        ips.push(pt);
      }
    }
  }
  return ips;
}
function intersectLine2Arc(line, arc) {
  let ip = [];
  if (intersectLine2Box(line, arc.box).length === 0) {
    return ip;
  }
  let circle = new Flatten.Circle(arc.pc, arc.r);
  let ip_tmp = intersectLine2Circle(line, circle);
  for (let pt of ip_tmp) {
    if (pt.on(arc)) {
      ip.push(pt);
    }
  }
  return ip;
}
function intersectSegment2Line(seg, line) {
  let ip = [];
  if (seg.ps.on(line)) {
    ip.push(seg.ps);
  }
  if (seg.pe.on(line) && !seg.isZeroLength()) {
    ip.push(seg.pe);
  }
  if (ip.length > 0) {
    return ip;
  }
  if (seg.isZeroLength()) {
    return ip;
  }
  if (seg.ps.leftTo(line) && seg.pe.leftTo(line) || !seg.ps.leftTo(line) && !seg.pe.leftTo(line)) {
    return ip;
  }
  let line1 = new Flatten.Line(seg.ps, seg.pe);
  return intersectLine2Line(line1, line);
}
function intersectSegment2Segment(seg1, seg2) {
  let ip = [];
  if (seg1.isZeroLength()) {
    if (seg1.ps.on(seg2)) {
      ip.push(seg1.ps);
    }
    return ip;
  }
  if (seg2.isZeroLength()) {
    if (seg2.ps.on(seg1)) {
      ip.push(seg2.ps);
    }
    return ip;
  }
  let line1 = new Flatten.Line(seg1.ps, seg1.pe);
  let line2 = new Flatten.Line(seg2.ps, seg2.pe);
  if (line1.incidentTo(line2)) {
    if (seg1.ps.on(seg2)) {
      ip.push(seg1.ps);
    }
    if (seg1.pe.on(seg2)) {
      ip.push(seg1.pe);
    }
    if (seg2.ps.on(seg1) && !seg2.ps.equalTo(seg1.ps) && !seg2.ps.equalTo(seg1.pe)) {
      ip.push(seg2.ps);
    }
    if (seg2.pe.on(seg1) && !seg2.pe.equalTo(seg1.ps) && !seg2.pe.equalTo(seg1.pe)) {
      ip.push(seg2.pe);
    }
  } else if (line1.parallelTo(line2)) {
    const r = new Flatten.Vector(seg1.ps, seg1.pe);
    const s = new Flatten.Vector(seg2.ps, seg2.pe);
    const q_p = new Flatten.Vector(seg1.ps, seg2.ps);
    const r_cross_s = r.cross(s);
    if (!Flatten.Utils.EQ_0(r_cross_s)) {
      const t = q_p.cross(s) / r_cross_s;
      const u = q_p.cross(r) / r_cross_s;
      if (Flatten.Utils.GE(t, 0) && Flatten.Utils.LE(t, 1) && Flatten.Utils.GE(u, 0) && Flatten.Utils.LE(u, 1)) {
        ip.push(snapToSegmentEndpoints(seg1.ps.translate(r.multiply(t)), seg1, seg2));
      }
    }
  } else {
    let new_ip = intersectLine2Line(line1, line2);
    if (new_ip.length > 0) {
      if (isPointInSegmentBox(new_ip[0], seg1) && isPointInSegmentBox(new_ip[0], seg2)) {
        ip.push(snapToSegmentEndpoints(new_ip[0], seg1, seg2));
      }
    }
  }
  return ip;
}
function snapToSegmentEndpoints(pt, seg1, seg2) {
  for (const endpoint of [seg1.ps, seg1.pe, seg2.ps, seg2.pe]) {
    if (pt.equalTo(endpoint)) {
      return endpoint;
    }
  }
  return pt;
}
function isPointInSegmentBox(point, segment) {
  const box = segment.box;
  return Flatten.Utils.LE(point.x, box.xmax) && Flatten.Utils.GE(point.x, box.xmin) && Flatten.Utils.LE(point.y, box.ymax) && Flatten.Utils.GE(point.y, box.ymin);
}
function intersectSegment2Circle(segment, circle) {
  let ips = [];
  if (segment.isZeroLength()) {
    let [dist, _] = segment.ps.distanceTo(circle.pc);
    if (Flatten.Utils.EQ(dist, circle.r)) {
      ips.push(segment.ps);
    }
    return ips;
  }
  let line = new Flatten.Line(segment.ps, segment.pe);
  let ips_tmp = intersectLine2Circle(line, circle);
  for (let ip of ips_tmp) {
    if (ip.on(segment)) {
      ips.push(ip);
    }
  }
  return ips;
}
function intersectSegment2Arc(segment, arc) {
  let ip = [];
  if (segment.isZeroLength()) {
    if (segment.ps.on(arc)) {
      ip.push(segment.ps);
    }
    return ip;
  }
  let line = new Flatten.Line(segment.ps, segment.pe);
  let circle = new Flatten.Circle(arc.pc, arc.r);
  let ip_tmp = intersectLine2Circle(line, circle);
  for (let pt of ip_tmp) {
    if (pt.on(segment) && pt.on(arc)) {
      ip.push(pt);
    }
  }
  return ip;
}
function intersectSegment2Box(segment, box) {
  let ips = [];
  for (let seg of box.toSegments()) {
    let ips_tmp = intersectSegment2Segment(seg, segment);
    for (let ip of ips_tmp) {
      ips.push(ip);
    }
  }
  return ips;
}
function intersectCircle2Circle(circle1, circle2) {
  let ip = [];
  let vec = new Flatten.Vector(circle1.pc, circle2.pc);
  let r1 = circle1.r;
  let r2 = circle2.r;
  if (Flatten.Utils.EQ_0(r1) || Flatten.Utils.EQ_0(r2))
    return ip;
  if (Flatten.Utils.EQ_0(vec.x) && Flatten.Utils.EQ_0(vec.y) && Flatten.Utils.EQ(r1, r2)) {
    ip.push(circle1.pc.translate(-r1, 0));
    return ip;
  }
  let dist = circle1.pc.distanceTo(circle2.pc)[0];
  if (Flatten.Utils.GT(dist, r1 + r2))
    return ip;
  if (Flatten.Utils.LT(dist, Math.abs(r1 - r2)))
    return ip;
  vec.x /= dist;
  vec.y /= dist;
  let pt;
  if (Flatten.Utils.EQ(dist, r1 + r2) || Flatten.Utils.EQ(dist, Math.abs(r1 - r2))) {
    pt = circle1.pc.translate(r1 * vec.x, r1 * vec.y);
    ip.push(pt);
    return ip;
  }
  let a = r1 * r1 / (2 * dist) - r2 * r2 / (2 * dist) + dist / 2;
  let mid_pt = circle1.pc.translate(a * vec.x, a * vec.y);
  let h = Math.sqrt(r1 * r1 - a * a);
  pt = mid_pt.translate(vec.rotate90CCW().multiply(h));
  ip.push(pt);
  pt = mid_pt.translate(vec.rotate90CW().multiply(h));
  ip.push(pt);
  return ip;
}
function intersectCircle2Box(circle, box) {
  let ips = [];
  for (let seg of box.toSegments()) {
    let ips_tmp = intersectSegment2Circle(seg, circle);
    for (let ip of ips_tmp) {
      ips.push(ip);
    }
  }
  return ips;
}
function intersectArc2Arc(arc1, arc2) {
  let ip = [];
  if (arc1.pc.equalTo(arc2.pc) && Flatten.Utils.EQ(arc1.r, arc2.r)) {
    let pt;
    pt = arc1.start;
    if (pt.on(arc2))
      ip.push(pt);
    pt = arc1.end;
    if (pt.on(arc2))
      ip.push(pt);
    pt = arc2.start;
    if (pt.on(arc1))
      ip.push(pt);
    pt = arc2.end;
    if (pt.on(arc1))
      ip.push(pt);
    return ip;
  }
  let circle1 = new Flatten.Circle(arc1.pc, arc1.r);
  let circle2 = new Flatten.Circle(arc2.pc, arc2.r);
  let ip_tmp = circle1.intersect(circle2);
  for (let pt of ip_tmp) {
    if (pt.on(arc1) && pt.on(arc2)) {
      ip.push(pt);
    }
  }
  return ip;
}
function intersectArc2Circle(arc, circle) {
  let ip = [];
  if (circle.pc.equalTo(arc.pc) && Flatten.Utils.EQ(circle.r, arc.r)) {
    ip.push(arc.start);
    ip.push(arc.end);
    return ip;
  }
  let circle1 = circle;
  let circle2 = new Flatten.Circle(arc.pc, arc.r);
  let ip_tmp = intersectCircle2Circle(circle1, circle2);
  for (let pt of ip_tmp) {
    if (pt.on(arc)) {
      ip.push(pt);
    }
  }
  return ip;
}
function intersectArc2Box(arc, box) {
  let ips = [];
  for (let seg of box.toSegments()) {
    let ips_tmp = intersectSegment2Arc(seg, arc);
    for (let ip of ips_tmp) {
      ips.push(ip);
    }
  }
  return ips;
}
function intersectEdge2Segment(edge, segment) {
  return edge.isSegment ? intersectSegment2Segment(edge.shape, segment) : intersectSegment2Arc(segment, edge.shape);
}
function intersectEdge2Arc(edge, arc) {
  return edge.isSegment ? intersectSegment2Arc(edge.shape, arc) : intersectArc2Arc(edge.shape, arc);
}
function intersectEdge2Line(edge, line) {
  return edge.isSegment ? intersectSegment2Line(edge.shape, line) : intersectLine2Arc(line, edge.shape);
}
function intersectEdge2Ray(edge, ray) {
  return edge.isSegment ? intersectRay2Segment(ray, edge.shape) : intersectRay2Arc(ray, edge.shape);
}
function intersectEdge2Circle(edge, circle) {
  return edge.isSegment ? intersectSegment2Circle(edge.shape, circle) : intersectArc2Circle(edge.shape, circle);
}
function intersectSegment2Polygon(segment, polygon) {
  let ip = [];
  for (let edge of polygon.edges) {
    for (let pt of intersectEdge2Segment(edge, segment)) {
      ip.push(pt);
    }
  }
  return ip;
}
function intersectArc2Polygon(arc, polygon) {
  let ip = [];
  for (let edge of polygon.edges) {
    for (let pt of intersectEdge2Arc(edge, arc)) {
      ip.push(pt);
    }
  }
  return ip;
}
function intersectLine2Polygon(line, polygon) {
  let ip = [];
  if (polygon.isEmpty()) {
    return ip;
  }
  for (let edge of polygon.edges) {
    for (let pt of intersectEdge2Line(edge, line)) {
      if (!ptInIntPoints(pt, ip)) {
        ip.push(pt);
      }
    }
  }
  return line.sortPoints(ip);
}
function intersectCircle2Polygon(circle, polygon) {
  let ip = [];
  if (polygon.isEmpty()) {
    return ip;
  }
  for (let edge of polygon.edges) {
    for (let pt of intersectEdge2Circle(edge, circle)) {
      ip.push(pt);
    }
  }
  return ip;
}
function intersectEdge2Edge(edge1, edge2) {
  if (edge1.isSegment) {
    return intersectEdge2Segment(edge2, edge1.shape);
  } else if (edge1.isArc) {
    return intersectEdge2Arc(edge2, edge1.shape);
  } else if (edge1.isLine) {
    return intersectEdge2Line(edge2, edge1.shape);
  } else if (edge1.isRay) {
    return intersectEdge2Ray(edge2, edge1.shape);
  }
  return [];
}
function intersectEdge2Polygon(edge, polygon) {
  let ip = [];
  if (polygon.isEmpty() || edge.shape.box.not_intersect(polygon.box)) {
    return ip;
  }
  let resp_edges = polygon.edges.search(edge.shape.box);
  for (let resp_edge of resp_edges) {
    ip = [...ip, ...intersectEdge2Edge(edge, resp_edge)];
  }
  return ip;
}
function intersectMultiline2Polygon(multiline, polygon) {
  let ip = [];
  if (polygon.isEmpty() || multiline.size === 0) {
    return ip;
  }
  for (let edge of multiline) {
    ip = [...ip, ...intersectEdge2Polygon(edge, polygon)];
  }
  return ip;
}
function intersectPolygon2Polygon(polygon1, polygon2) {
  let ip = [];
  if (polygon1.isEmpty() || polygon2.isEmpty()) {
    return ip;
  }
  if (polygon1.box.not_intersect(polygon2.box)) {
    return ip;
  }
  for (let edge1 of polygon1.edges) {
    ip = [...ip, ...intersectEdge2Polygon(edge1, polygon2)];
  }
  return ip;
}
function intersectShape2Polygon(shape, polygon) {
  if (shape instanceof Flatten.Line) {
    return intersectLine2Polygon(shape, polygon);
  } else if (shape instanceof Flatten.Segment) {
    return intersectSegment2Polygon(shape, polygon);
  } else if (shape instanceof Flatten.Arc) {
    return intersectArc2Polygon(shape, polygon);
  } else {
    return [];
  }
}
function ptInIntPoints(new_pt, ip) {
  return ip.some((pt) => pt.equalTo(new_pt));
}
function createLineFromRay(ray) {
  return new Flatten.Line(ray.start, ray.norm);
}
function intersectRay2Segment(ray, segment) {
  return intersectSegment2Line(segment, createLineFromRay(ray)).filter((pt) => ray.contains(pt));
}
function intersectRay2Arc(ray, arc) {
  return intersectLine2Arc(createLineFromRay(ray), arc).filter((pt) => ray.contains(pt));
}
function intersectRay2Circle(ray, circle) {
  return intersectLine2Circle(createLineFromRay(ray), circle).filter((pt) => ray.contains(pt));
}
function intersectRay2Box(ray, box) {
  return intersectLine2Box(createLineFromRay(ray), box).filter((pt) => ray.contains(pt));
}
function intersectRay2Line(ray, line) {
  return intersectLine2Line(createLineFromRay(ray), line).filter((pt) => ray.contains(pt));
}
function intersectRay2Ray(ray1, ray2) {
  return intersectLine2Line(createLineFromRay(ray1), createLineFromRay(ray2)).filter((pt) => ray1.contains(pt)).filter((pt) => ray2.contains(pt));
}
function intersectRay2Polygon(ray, polygon) {
  return intersectLine2Polygon(createLineFromRay(ray), polygon).filter((pt) => ray.contains(pt));
}
function intersectShape2Shape(shape1, shape2) {
  if (shape1.intersect && shape1.intersect instanceof Function) {
    return shape1.intersect(shape2);
  }
  throw Errors.UNSUPPORTED_SHAPE_TYPE;
}
function intersectShape2Multiline(shape, multiline) {
  let ip = [];
  for (let edge of multiline) {
    ip = [...ip, ...intersectShape2Shape(shape, edge.shape)];
  }
  return ip;
}
function intersectMultiline2Multiline(multiline1, multiline2) {
  let ip = [];
  for (let edge1 of multiline1) {
    for (let edge2 of multiline2) {
      ip = [...ip, ...intersectShape2Shape(edge1.shape, edge2.shape)];
    }
  }
  return ip;
}
var Multiline$1 = class Multiline extends LinkedList {
  constructor(...args) {
    super();
    this.isInfinite = false;
    if (args.length === 1 && args[0] instanceof Array && args[0].length > 0) {
      const shapes = args[0];
      const L = shapes.length;
      const anyShape = (s) => s instanceof Flatten.Segment || s instanceof Flatten.Arc || s instanceof Flatten.Ray || s instanceof Flatten.Line;
      const anyShapeExceptLine = (s) => s instanceof Flatten.Segment || s instanceof Flatten.Arc || s instanceof Flatten.Ray;
      const shapeSegmentOrArc = (s) => s instanceof Flatten.Segment || s instanceof Flatten.Arc;
      const validShapes = L === 1 && anyShape(shapes[0]) || L > 1 && anyShapeExceptLine(shapes[0]) && anyShapeExceptLine(shapes[L - 1]) && shapes.slice(1, L - 1).every(shapeSegmentOrArc);
      if (validShapes) {
        this.isInfinite = shapes.some((shape) => shape instanceof Flatten.Ray || shape instanceof Flatten.Line);
        for (let shape of shapes) {
          let edge = new Flatten.Edge(shape);
          this.append(edge);
        }
        this.setArcLength();
      } else {
        throw Flatten.Errors.ILLEGAL_PARAMETERS;
      }
    }
  }
  get edges() {
    return [...this];
  }
  get box() {
    return this.edges.reduce((acc, edge) => acc.merge(edge.box), new Flatten.Box);
  }
  get vertices() {
    let v = this.edges.map((edge) => edge.start);
    v.push(this.last.end);
    return v;
  }
  get length() {
    if (this.isEmpty())
      return 0;
    if (this.isInfinite)
      return Number.POSITIVE_INFINITY;
    let len = 0;
    for (let edge of this) {
      len += edge.length;
    }
    return len;
  }
  clone() {
    return new Multiline(this.toShapes());
  }
  setArcLength() {
    for (let edge of this) {
      this.setOneEdgeArcLength(edge);
    }
  }
  setOneEdgeArcLength(edge) {
    if (edge === this.first) {
      edge.arc_length = 0;
    } else {
      edge.arc_length = edge.prev.arc_length + edge.prev.length;
    }
  }
  pointAtLength(length) {
    if (length > this.length || length < 0)
      return null;
    if (this.isInfinite)
      return null;
    let point = null;
    for (let edge of this) {
      if (length >= edge.arc_length && (edge === this.last || length < edge.next.arc_length)) {
        point = edge.pointAtLength(length - edge.arc_length);
        break;
      }
    }
    return point;
  }
  addVertex(pt, edge) {
    let shapes = edge.shape.split(pt);
    if (shapes[0] === null)
      return edge.prev;
    if (shapes[1] === null)
      return edge;
    let newEdge = new Flatten.Edge(shapes[0]);
    let edgeBefore = edge.prev;
    this.insert(newEdge, edgeBefore);
    edge.shape = shapes[1];
    return newEdge;
  }
  getChain(edgeFrom, edgeTo) {
    let edges = [];
    for (let edge = edgeFrom;edge !== edgeTo.next; edge = edge.next) {
      edges.push(edge);
    }
    return edges;
  }
  split(ip) {
    for (let pt of ip) {
      let edge = this.findEdgeByPoint(pt);
      this.addVertex(pt, edge);
    }
    return this;
  }
  findEdgeByPoint(pt) {
    let edgeFound;
    for (let edge of this) {
      if (edge.shape.contains(pt)) {
        edgeFound = edge;
        break;
      }
    }
    return edgeFound;
  }
  distanceTo(shape) {
    if (shape instanceof Flatten.Point) {
      const [dist, shortest_segment] = Flatten.Distance.shape2multiline(shape, this);
      return [dist, shortest_segment.reverse()];
    }
    if (shape instanceof Flatten.Line) {
      const [dist, shortest_segment] = Flatten.Distance.shape2multiline(shape, this);
      return [dist, shortest_segment.reverse()];
    }
    if (shape instanceof Flatten.Circle) {
      const [dist, shortest_segment] = Flatten.Distance.shape2multiline(shape, this);
      return [dist, shortest_segment.reverse()];
    }
    if (shape instanceof Flatten.Segment) {
      const [dist, shortest_segment] = Flatten.Distance.shape2multiline(shape, this);
      return [dist, shortest_segment.reverse()];
    }
    if (shape instanceof Flatten.Arc) {
      const [dist, shortest_segment] = Flatten.Distance.shape2multiline(shape, this);
      return [dist, shortest_segment.reverse()];
    }
    if (shape instanceof Flatten.Box) {
      const [dist, shortest_segment] = Flatten.Distance.shape2multiline(new Flatten.Polygon(shape), this);
      return [dist, shortest_segment.reverse()];
    }
    if (shape instanceof Flatten.Multiline) {
      return Flatten.Distance.multiline2multiline(this, shape);
    }
    throw Flatten.Errors.UNSUPPORTED_SHAPE_TYPE;
  }
  intersect(shape) {
    if (shape instanceof Flatten.Multiline) {
      return intersectMultiline2Multiline(this, shape);
    } else {
      return intersectShape2Multiline(shape, this);
    }
  }
  contains(shape) {
    if (shape instanceof Flatten.Point) {
      return this.edges.some((edge) => edge.shape.contains(shape));
    }
    throw Flatten.Errors.UNSUPPORTED_SHAPE_TYPE;
  }
  translate(vec) {
    return new Multiline(this.edges.map((edge) => edge.shape.translate(vec)));
  }
  rotate(angle = 0, center = new Flatten.Point) {
    return new Multiline(this.edges.map((edge) => edge.shape.rotate(angle, center)));
  }
  transform(matrix = new Flatten.Matrix) {
    return new Multiline(this.edges.map((edge) => edge.shape.transform(matrix)));
  }
  toShapes() {
    return this.edges.map((edge) => edge.shape.clone());
  }
  toJSON() {
    return this.edges.map((edge) => edge.toJSON());
  }
  svgPoints() {
    return this.vertices.map((p) => `${p.x},${p.y}`).join(" ");
  }
  dpath() {
    let dPathStr = `M${this.first.start.x},${this.first.start.y}`;
    for (let edge of this) {
      dPathStr += edge.svg();
    }
    return dPathStr;
  }
  svg(attrs = {}) {
    let svgStr = `
<path ${convertToString({ fill: "none", ...attrs })} d="`;
    svgStr += `
M${this.first.start.x},${this.first.start.y}`;
    for (let edge of this) {
      svgStr += edge.svg();
    }
    svgStr += `" >
</path>`;
    return svgStr;
  }
};
Flatten.Multiline = Multiline$1;
var multiline = (...args) => new Flatten.Multiline(...args);
Flatten.multiline = multiline;
function addToIntPoints(edge, pt, int_points) {
  let id = int_points.length;
  let shapes = edge.shape.split(pt);
  if (shapes.length === 0)
    return;
  let len = 0;
  if (shapes[0] === null) {
    len = 0;
  } else if (shapes[1] === null) {
    len = edge.shape.length;
  } else {
    len = shapes[0].length;
  }
  let is_vertex = NOT_VERTEX$1;
  if (EQ(len, 0)) {
    is_vertex |= START_VERTEX$1;
  }
  if (EQ(len, edge.shape.length)) {
    is_vertex |= END_VERTEX$1;
  }
  let arc_length;
  if (len === Infinity) {
    arc_length = shapes[0].coord(pt);
  } else {
    arc_length = is_vertex & END_VERTEX$1 && edge.next && edge.next.arc_length === 0 ? 0 : edge.arc_length + len;
  }
  int_points.push({
    id,
    pt,
    arc_length,
    edge_before: edge,
    edge_after: undefined,
    face: edge.face,
    is_vertex
  });
}
function sortIntersections(intersections) {
  intersections.int_points1_sorted = getSortedArray(intersections.int_points1);
  intersections.int_points2_sorted = getSortedArray(intersections.int_points2);
}
function getSortedArray(int_points) {
  let faceMap = new Map;
  let id = 0;
  for (let ip of int_points) {
    if (!faceMap.has(ip.face)) {
      faceMap.set(ip.face, id);
      id++;
    }
  }
  for (let ip of int_points) {
    ip.faceId = faceMap.get(ip.face);
  }
  let int_points_sorted = int_points.slice().sort(compareFn);
  return int_points_sorted;
}
function compareFn(ip1, ip2) {
  if (ip1.faceId < ip2.faceId) {
    return -1;
  }
  if (ip1.faceId > ip2.faceId) {
    return 1;
  }
  if (ip1.arc_length < ip2.arc_length) {
    return -1;
  }
  if (ip1.arc_length > ip2.arc_length) {
    return 1;
  }
  return 0;
}
function filterDuplicatedIntersections(intersections) {
  if (intersections.int_points1.length < 2)
    return;
  let do_squeeze = false;
  let int_point_ref1;
  let int_point_ref2;
  let int_point_cur1;
  let int_point_cur2;
  for (let i = 0;i < intersections.int_points1_sorted.length; i++) {
    if (intersections.int_points1_sorted[i].id === -1)
      continue;
    int_point_ref1 = intersections.int_points1_sorted[i];
    int_point_ref2 = intersections.int_points2[int_point_ref1.id];
    for (let j = i + 1;j < intersections.int_points1_sorted.length; j++) {
      int_point_cur1 = intersections.int_points1_sorted[j];
      if (!EQ(int_point_cur1.arc_length, int_point_ref1.arc_length)) {
        break;
      }
      if (int_point_cur1.id === -1)
        continue;
      int_point_cur2 = intersections.int_points2[int_point_cur1.id];
      if (int_point_cur2.id === -1)
        continue;
      if (int_point_cur1.edge_before === int_point_ref1.edge_before && int_point_cur1.edge_after === int_point_ref1.edge_after && int_point_cur2.edge_before === int_point_ref2.edge_before && int_point_cur2.edge_after === int_point_ref2.edge_after) {
        int_point_cur1.id = -1;
        int_point_cur2.id = -1;
        do_squeeze = true;
      }
    }
  }
  int_point_ref2 = intersections.int_points2_sorted[0];
  int_point_ref1 = intersections.int_points1[int_point_ref2.id];
  for (let i = 1;i < intersections.int_points2_sorted.length; i++) {
    let int_point_cur2 = intersections.int_points2_sorted[i];
    if (int_point_cur2.id === -1)
      continue;
    if (int_point_ref2.id === -1 || !EQ(int_point_cur2.arc_length, int_point_ref2.arc_length)) {
      int_point_ref2 = int_point_cur2;
      int_point_ref1 = intersections.int_points1[int_point_ref2.id];
      continue;
    }
    let int_point_cur1 = intersections.int_points1[int_point_cur2.id];
    if (int_point_cur1.edge_before === int_point_ref1.edge_before && int_point_cur1.edge_after === int_point_ref1.edge_after && int_point_cur2.edge_before === int_point_ref2.edge_before && int_point_cur2.edge_after === int_point_ref2.edge_after) {
      int_point_cur1.id = -1;
      int_point_cur2.id = -1;
      do_squeeze = true;
    }
  }
  if (do_squeeze) {
    intersections.int_points1 = intersections.int_points1.filter((int_point) => int_point.id >= 0);
    intersections.int_points2 = intersections.int_points2.filter((int_point) => int_point.id >= 0);
    intersections.int_points1.forEach((int_point, index) => int_point.id = index);
    intersections.int_points2.forEach((int_point, index) => int_point.id = index);
  }
}
function initializeInclusionFlags(int_points) {
  for (let int_point of int_points) {
    if (int_point.edge_before) {
      int_point.edge_before.bvStart = undefined;
      int_point.edge_before.bvEnd = undefined;
      int_point.edge_before.bv = undefined;
      int_point.edge_before.overlap = undefined;
    }
    if (int_point.edge_after) {
      int_point.edge_after.bvStart = undefined;
      int_point.edge_after.bvEnd = undefined;
      int_point.edge_after.bv = undefined;
      int_point.edge_after.overlap = undefined;
    }
  }
  for (let int_point of int_points) {
    if (int_point.edge_before)
      int_point.edge_before.bvEnd = BOUNDARY$1;
    if (int_point.edge_after)
      int_point.edge_after.bvStart = BOUNDARY$1;
  }
}
function calculateInclusionFlags(int_points, polygon) {
  for (let int_point of int_points) {
    if (int_point.edge_before)
      int_point.edge_before.setInclusion(polygon);
    if (int_point.edge_after)
      int_point.edge_after.setInclusion(polygon);
  }
}
function setOverlappingFlags(intersections) {
  let cur_face = undefined;
  let first_int_point_in_face_id = undefined;
  let next_int_point1 = undefined;
  let num_int_points = intersections.int_points1.length;
  for (let i = 0;i < num_int_points; i++) {
    let cur_int_point1 = intersections.int_points1_sorted[i];
    if (cur_int_point1.face !== cur_face) {
      first_int_point_in_face_id = i;
      cur_face = cur_int_point1.face;
    }
    let int_points_cur_pool_start = i;
    let int_points_cur_pool_num = intPointsPoolCount(intersections.int_points1_sorted, i, cur_face);
    let next_int_point_id;
    if (int_points_cur_pool_start + int_points_cur_pool_num < num_int_points && intersections.int_points1_sorted[int_points_cur_pool_start + int_points_cur_pool_num].face === cur_face) {
      next_int_point_id = int_points_cur_pool_start + int_points_cur_pool_num;
    } else {
      next_int_point_id = first_int_point_in_face_id;
    }
    let int_points_next_pool_num = intPointsPoolCount(intersections.int_points1_sorted, next_int_point_id, cur_face);
    next_int_point1 = null;
    for (let j = next_int_point_id;j < next_int_point_id + int_points_next_pool_num; j++) {
      let next_int_point1_tmp = intersections.int_points1_sorted[j];
      if (next_int_point1_tmp.face === cur_face && intersections.int_points2[next_int_point1_tmp.id].face === intersections.int_points2[cur_int_point1.id].face) {
        next_int_point1 = next_int_point1_tmp;
        break;
      }
    }
    if (next_int_point1 === null)
      continue;
    let edge_from1 = cur_int_point1.edge_after;
    let edge_to1 = next_int_point1.edge_before;
    if (!(edge_from1.bv === BOUNDARY$1 && edge_to1.bv === BOUNDARY$1))
      continue;
    if (edge_from1 !== edge_to1)
      continue;
    let cur_int_point2 = intersections.int_points2[cur_int_point1.id];
    let next_int_point2 = intersections.int_points2[next_int_point1.id];
    let edge_from2 = cur_int_point2.edge_after;
    let edge_to2 = next_int_point2.edge_before;
    if (!(edge_from2.bv === BOUNDARY$1 && edge_to2.bv === BOUNDARY$1 && edge_from2 === edge_to2)) {
      cur_int_point2 = intersections.int_points2[next_int_point1.id];
      next_int_point2 = intersections.int_points2[cur_int_point1.id];
      edge_from2 = cur_int_point2.edge_after;
      edge_to2 = next_int_point2.edge_before;
    }
    if (!(edge_from2.bv === BOUNDARY$1 && edge_to2.bv === BOUNDARY$1 && edge_from2 === edge_to2))
      continue;
    edge_from1.setOverlap(edge_from2);
  }
}
function intPointsPoolCount(int_points, cur_int_point_num, cur_face) {
  let int_point_current;
  let int_point_next;
  let int_points_pool_num = 1;
  if (int_points.length === 1)
    return 1;
  int_point_current = int_points[cur_int_point_num];
  for (let i = cur_int_point_num + 1;i < int_points.length; i++) {
    if (int_point_current.face !== cur_face) {
      break;
    }
    int_point_next = int_points[i];
    if (!(int_point_next.pt.equalTo(int_point_current.pt) && int_point_next.edge_before === int_point_current.edge_before && int_point_next.edge_after === int_point_current.edge_after)) {
      break;
    }
    int_points_pool_num++;
  }
  return int_points_pool_num;
}
function splitByIntersections(polygon, int_points) {
  if (!int_points)
    return;
  for (let int_point of int_points) {
    let edge = int_point.edge_before;
    int_point.is_vertex = NOT_VERTEX$1;
    if (edge.shape.start && edge.shape.start.equalTo(int_point.pt)) {
      int_point.is_vertex |= START_VERTEX$1;
    }
    if (edge.shape.end && edge.shape.end.equalTo(int_point.pt)) {
      int_point.is_vertex |= END_VERTEX$1;
    }
    if (int_point.is_vertex & START_VERTEX$1) {
      int_point.edge_before = edge.prev;
      if (edge.prev) {
        int_point.is_vertex = END_VERTEX$1;
      }
      continue;
    }
    if (int_point.is_vertex & END_VERTEX$1) {
      continue;
    }
    let newEdge = polygon.addVertex(int_point.pt, edge);
    int_point.edge_before = newEdge;
  }
  for (let int_point of int_points) {
    if (int_point.edge_before) {
      int_point.edge_after = int_point.edge_before.next;
    } else {
      if (polygon instanceof Multiline$1 && int_point.is_vertex & START_VERTEX$1) {
        int_point.edge_after = polygon.first;
      }
    }
  }
}
function insertBetweenIntPoints(int_point1, int_point2, new_edges) {
  const edge_before = int_point1.edge_before;
  const edge_after = int_point2.edge_after;
  const len = new_edges.length;
  edge_before.next = new_edges[0];
  new_edges[0].prev = edge_before;
  new_edges[len - 1].next = edge_after;
  edge_after.prev = new_edges[len - 1];
}
var { INSIDE: INSIDE$1, OUTSIDE, BOUNDARY, OVERLAP_SAME, OVERLAP_OPPOSITE } = Constants;
var { NOT_VERTEX, START_VERTEX, END_VERTEX } = Constants;
var BOOLEAN_UNION = 1;
var BOOLEAN_INTERSECT = 2;
var BOOLEAN_SUBTRACT = 3;
function unify(polygon1, polygon2) {
  let [res_poly, wrk_poly] = booleanOpBinary(polygon1, polygon2, BOOLEAN_UNION, true);
  return res_poly;
}
function subtract(polygon1, polygon2) {
  let polygon2_tmp = polygon2.clone();
  let polygon2_reversed = polygon2_tmp.reverse();
  let [res_poly, wrk_poly] = booleanOpBinary(polygon1, polygon2_reversed, BOOLEAN_SUBTRACT, true);
  return res_poly;
}
function intersect$1(polygon1, polygon2) {
  let [res_poly, wrk_poly] = booleanOpBinary(polygon1, polygon2, BOOLEAN_INTERSECT, true);
  return res_poly;
}
function innerClip(polygon1, polygon2) {
  let [res_poly, wrk_poly] = booleanOpBinary(polygon1, polygon2, BOOLEAN_INTERSECT, false);
  let clip_shapes1 = [];
  for (let face of res_poly.faces) {
    clip_shapes1 = [...clip_shapes1, ...[...face.edges].map((edge) => edge.shape)];
  }
  let clip_shapes2 = [];
  for (let face of wrk_poly.faces) {
    clip_shapes2 = [...clip_shapes2, ...[...face.edges].map((edge) => edge.shape)];
  }
  return [clip_shapes1, clip_shapes2];
}
function outerClip(polygon1, polygon2) {
  let [res_poly, wrk_poly] = booleanOpBinary(polygon1, polygon2, BOOLEAN_SUBTRACT, false);
  let clip_shapes1 = [];
  for (let face of res_poly.faces) {
    clip_shapes1 = [...clip_shapes1, ...[...face.edges].map((edge) => edge.shape)];
  }
  return clip_shapes1;
}
function calculateIntersections(polygon1, polygon2) {
  let res_poly = polygon1.clone();
  let wrk_poly = polygon2.clone();
  let intersections = getIntersections(res_poly, wrk_poly);
  sortIntersections(intersections);
  splitByIntersections(res_poly, intersections.int_points1_sorted);
  splitByIntersections(wrk_poly, intersections.int_points2_sorted);
  filterDuplicatedIntersections(intersections);
  sortIntersections(intersections);
  let ip_sorted1 = intersections.int_points1_sorted.map((int_point) => int_point.pt);
  let ip_sorted2 = intersections.int_points2_sorted.map((int_point) => int_point.pt);
  return [ip_sorted1, ip_sorted2];
}
function filterNotRelevantEdges(res_poly, wrk_poly, intersections, op) {
  let notIntersectedFacesRes = getNotIntersectedFaces(res_poly, intersections.int_points1);
  let notIntersectedFacesWrk = getNotIntersectedFaces(wrk_poly, intersections.int_points2);
  calcInclusionForNotIntersectedFaces(notIntersectedFacesRes, wrk_poly);
  calcInclusionForNotIntersectedFaces(notIntersectedFacesWrk, res_poly);
  initializeInclusionFlags(intersections.int_points1);
  initializeInclusionFlags(intersections.int_points2);
  calculateInclusionFlags(intersections.int_points1, wrk_poly);
  calculateInclusionFlags(intersections.int_points2, res_poly);
  while (fixBoundaryConflicts(res_poly, wrk_poly, intersections.int_points1, intersections.int_points1_sorted, intersections.int_points2, intersections))
    ;
  setOverlappingFlags(intersections);
  removeNotRelevantChains(res_poly, op, intersections.int_points1_sorted, true);
  removeNotRelevantChains(wrk_poly, op, intersections.int_points2_sorted, false);
  removeNotRelevantNotIntersectedFaces(res_poly, notIntersectedFacesRes, op, true);
  removeNotRelevantNotIntersectedFaces(wrk_poly, notIntersectedFacesWrk, op, false);
}
function swapLinksAndRestore(res_poly, wrk_poly, intersections, op) {
  copyWrkToRes(res_poly, wrk_poly, op, intersections.int_points2);
  swapLinks(res_poly, wrk_poly, intersections);
  removeOldFaces(res_poly, intersections.int_points1);
  removeOldFaces(wrk_poly, intersections.int_points2);
  restoreFaces(res_poly, intersections.int_points1, intersections.int_points2);
  restoreFaces(res_poly, intersections.int_points2, intersections.int_points1);
  removeDetachedEdges(res_poly);
  removeDetachedEdges(wrk_poly);
}
function booleanOpBinary(polygon1, polygon2, op, restore) {
  let res_poly = polygon1.clone();
  let wrk_poly = polygon2.clone();
  let intersections = getIntersections(res_poly, wrk_poly);
  sortIntersections(intersections);
  splitByIntersections(res_poly, intersections.int_points1_sorted);
  splitByIntersections(wrk_poly, intersections.int_points2_sorted);
  filterDuplicatedIntersections(intersections);
  sortIntersections(intersections);
  filterNotRelevantEdges(res_poly, wrk_poly, intersections, op);
  if (restore) {
    swapLinksAndRestore(res_poly, wrk_poly, intersections, op);
  }
  return [res_poly, wrk_poly];
}
function getIntersections(polygon1, polygon2) {
  let intersections = {
    int_points1: [],
    int_points2: []
  };
  for (let edge1 of polygon1.edges) {
    let resp = polygon2.edges.search(edge1.box);
    for (let edge2 of resp) {
      let ip = edge1.shape.intersect(edge2.shape);
      for (let pt of ip) {
        addToIntPoints(edge1, pt, intersections.int_points1);
        addToIntPoints(edge2, pt, intersections.int_points2);
      }
    }
  }
  return intersections;
}
function getNotIntersectedFaces(poly, int_points) {
  let notIntersected = [];
  for (let face of poly.faces) {
    if (!int_points.find((ip) => ip.face === face)) {
      notIntersected.push(face);
    }
  }
  return notIntersected;
}
function calcInclusionForNotIntersectedFaces(notIntersectedFaces, poly2) {
  for (let face of notIntersectedFaces) {
    face.first.bv = face.first.bvStart = face.first.bvEnd = undefined;
    face.first.setInclusion(poly2);
  }
}
function fixBoundaryConflicts(poly1, poly2, int_points1, int_points1_sorted, int_points2, intersections) {
  let cur_face;
  let first_int_point_in_face_id;
  let next_int_point1;
  let num_int_points = int_points1_sorted.length;
  let iterate_more = false;
  for (let i = 0;i < num_int_points; i++) {
    let cur_int_point1 = int_points1_sorted[i];
    if (cur_int_point1.face !== cur_face) {
      first_int_point_in_face_id = i;
      cur_face = cur_int_point1.face;
    }
    let int_points_cur_pool_start = i;
    let int_points_cur_pool_num = intPointsPoolCount(int_points1_sorted, i, cur_face);
    let next_int_point_id;
    if (int_points_cur_pool_start + int_points_cur_pool_num < num_int_points && int_points1_sorted[int_points_cur_pool_start + int_points_cur_pool_num].face === cur_face) {
      next_int_point_id = int_points_cur_pool_start + int_points_cur_pool_num;
    } else {
      next_int_point_id = first_int_point_in_face_id;
    }
    let int_points_next_pool_num = intPointsPoolCount(int_points1_sorted, next_int_point_id, cur_face);
    next_int_point1 = null;
    for (let j = next_int_point_id;j < next_int_point_id + int_points_next_pool_num; j++) {
      let next_int_point1_tmp = int_points1_sorted[j];
      if (next_int_point1_tmp.face === cur_face && int_points2[next_int_point1_tmp.id].face === int_points2[cur_int_point1.id].face) {
        next_int_point1 = next_int_point1_tmp;
        break;
      }
    }
    if (next_int_point1 === null)
      continue;
    let edge_from1 = cur_int_point1.edge_after;
    let edge_to1 = next_int_point1.edge_before;
    if (edge_from1.bv === BOUNDARY && edge_to1.bv != BOUNDARY) {
      edge_from1.bv = edge_to1.bv;
      continue;
    }
    if (edge_from1.bv != BOUNDARY && edge_to1.bv === BOUNDARY) {
      edge_to1.bv = edge_from1.bv;
      continue;
    }
    if (edge_from1.bv === BOUNDARY && edge_to1.bv === BOUNDARY && edge_from1 != edge_to1 || (edge_from1.bv === INSIDE$1 && edge_to1.bv === OUTSIDE || edge_from1.bv === OUTSIDE && edge_to1.bv === INSIDE$1)) {
      let edge_tmp = edge_from1.next;
      while (edge_tmp != edge_to1) {
        edge_tmp.bvStart = undefined;
        edge_tmp.bvEnd = undefined;
        edge_tmp.bv = undefined;
        edge_tmp.setInclusion(poly2);
        edge_tmp = edge_tmp.next;
      }
    }
    if (edge_from1.bv === BOUNDARY && edge_to1.bv === BOUNDARY && edge_from1 != edge_to1) {
      let edge_tmp = edge_from1.next;
      let new_bv;
      while (edge_tmp != edge_to1) {
        if (edge_tmp.bv != BOUNDARY) {
          if (new_bv === undefined) {
            new_bv = edge_tmp.bv;
          } else {
            if (edge_tmp.bv != new_bv) {
              throw Errors.UNRESOLVED_BOUNDARY_CONFLICT;
            }
          }
        }
        edge_tmp = edge_tmp.next;
      }
      if (new_bv != null) {
        edge_from1.bv = new_bv;
        edge_to1.bv = new_bv;
      }
      continue;
    }
    if (edge_from1.bv === INSIDE$1 && edge_to1.bv === OUTSIDE || edge_from1.bv === OUTSIDE && edge_to1.bv === INSIDE$1) {
      let edge_tmp = edge_from1;
      while (edge_tmp != edge_to1) {
        if (edge_tmp.bvStart === edge_from1.bv && edge_tmp.bvEnd === edge_to1.bv) {
          let [dist, segment] = edge_tmp.shape.distanceTo(poly2);
          if (dist < 10 * Flatten.DP_TOL) {
            addToIntPoints(edge_tmp, segment.ps, int_points1);
            let int_point1 = int_points1[int_points1.length - 1];
            if (int_point1.is_vertex & START_VERTEX) {
              int_point1.edge_after = edge_tmp;
              int_point1.edge_before = edge_tmp.prev;
              edge_tmp.bvStart = BOUNDARY;
              edge_tmp.bv = undefined;
              edge_tmp.setInclusion(poly2);
            } else if (int_point1.is_vertex & END_VERTEX) {
              int_point1.edge_after = edge_tmp.next;
              edge_tmp.bvEnd = BOUNDARY;
              edge_tmp.bv = undefined;
              edge_tmp.setInclusion(poly2);
            } else {
              let newEdge1 = poly2.addVertex(int_point1.pt, edge_tmp);
              int_point1.edge_before = newEdge1;
              int_point1.edge_after = newEdge1.next;
              newEdge1.setInclusion(poly2);
              newEdge1.next.bvStart = BOUNDARY;
              newEdge1.next.bvEnd = undefined;
              newEdge1.next.bv = undefined;
              newEdge1.next.setInclusion(poly2);
            }
            let edge2 = poly2.findEdgeByPoint(segment.pe);
            addToIntPoints(edge2, segment.pe, int_points2);
            let int_point2 = int_points2[int_points2.length - 1];
            if (int_point2.is_vertex & START_VERTEX) {
              int_point2.edge_after = edge2;
              int_point2.edge_before = edge2.prev;
            } else if (int_point2.is_vertex & END_VERTEX) {
              int_point2.edge_after = edge2.next;
            } else {
              let int_point2_edge_after = int_points2.find((int_point) => int_point.edge_after === edge2);
              let newEdge2 = poly2.addVertex(int_point2.pt, edge2);
              int_point2.edge_before = newEdge2;
              int_point2.edge_after = newEdge2.next;
              if (int_point2_edge_after)
                int_point2_edge_after.edge_after = newEdge2;
              newEdge2.bvStart = undefined;
              newEdge2.bvEnd = BOUNDARY;
              newEdge2.bv = undefined;
              newEdge2.setInclusion(poly1);
              newEdge2.next.bvStart = BOUNDARY;
              newEdge2.next.bvEnd = undefined;
              newEdge2.next.bv = undefined;
              newEdge2.next.setInclusion(poly1);
            }
            sortIntersections(intersections);
            iterate_more = true;
            break;
          }
        }
        edge_tmp = edge_tmp.next;
      }
      if (iterate_more)
        break;
      throw Errors.UNRESOLVED_BOUNDARY_CONFLICT;
    }
  }
  return iterate_more;
}
function removeNotRelevantChains(polygon, op, int_points, is_res_polygon) {
  if (!int_points)
    return;
  let cur_face = undefined;
  let first_int_point_in_face_num = undefined;
  let int_point_current;
  let int_point_next;
  for (let i = 0;i < int_points.length; i++) {
    int_point_current = int_points[i];
    if (int_point_current.face !== cur_face) {
      first_int_point_in_face_num = i;
      cur_face = int_point_current.face;
    }
    if (cur_face.isEmpty())
      continue;
    let int_points_from_pull_start = i;
    let int_points_from_pull_num = intPointsPoolCount(int_points, i, cur_face);
    let next_int_point_num;
    if (int_points_from_pull_start + int_points_from_pull_num < int_points.length && int_points[int_points_from_pull_start + int_points_from_pull_num].face === int_point_current.face) {
      next_int_point_num = int_points_from_pull_start + int_points_from_pull_num;
    } else {
      next_int_point_num = first_int_point_in_face_num;
    }
    int_point_next = int_points[next_int_point_num];
    let int_points_to_pull_start = next_int_point_num;
    let int_points_to_pull_num = intPointsPoolCount(int_points, int_points_to_pull_start, cur_face);
    let edge_from = int_point_current.edge_after;
    let edge_to = int_point_next.edge_before;
    if (edge_from.bv === INSIDE$1 && edge_to.bv === INSIDE$1 && op === BOOLEAN_UNION || edge_from.bv === OUTSIDE && edge_to.bv === OUTSIDE && op === BOOLEAN_INTERSECT || (edge_from.bv === OUTSIDE || edge_to.bv === OUTSIDE) && op === BOOLEAN_SUBTRACT && !is_res_polygon || (edge_from.bv === INSIDE$1 || edge_to.bv === INSIDE$1) && op === BOOLEAN_SUBTRACT && is_res_polygon || edge_from.bv === BOUNDARY && edge_to.bv === BOUNDARY && edge_from.overlap & OVERLAP_SAME && is_res_polygon || edge_from.bv === BOUNDARY && edge_to.bv === BOUNDARY && edge_from.overlap & OVERLAP_OPPOSITE) {
      polygon.removeChain(cur_face, edge_from, edge_to);
      for (let k = int_points_from_pull_start;k < int_points_from_pull_start + int_points_from_pull_num; k++) {
        int_points[k].edge_after = undefined;
      }
      for (let k = int_points_to_pull_start;k < int_points_to_pull_start + int_points_to_pull_num; k++) {
        int_points[k].edge_before = undefined;
      }
    }
    i += int_points_from_pull_num - 1;
  }
}
function copyWrkToRes(res_polygon, wrk_polygon, op, int_points) {
  for (let face of wrk_polygon.faces) {
    for (let edge of face) {
      res_polygon.edges.add(edge);
    }
    if (int_points.find((ip) => ip.face === face) === undefined) {
      res_polygon.addFace(face.first, face.last);
    }
  }
}
function swapLinks(res_polygon, wrk_polygon, intersections) {
  if (intersections.int_points1.length === 0)
    return;
  for (let i = 0;i < intersections.int_points1.length; i++) {
    let int_point1 = intersections.int_points1[i];
    let int_point2 = intersections.int_points2[i];
    if (int_point1.edge_before !== undefined && int_point1.edge_after === undefined) {
      if (int_point2.edge_before === undefined && int_point2.edge_after !== undefined) {
        int_point1.edge_before.next = int_point2.edge_after;
        int_point2.edge_after.prev = int_point1.edge_before;
        int_point1.edge_after = int_point2.edge_after;
        int_point2.edge_before = int_point1.edge_before;
      }
    }
    if (int_point2.edge_before !== undefined && int_point2.edge_after === undefined) {
      if (int_point1.edge_before === undefined && int_point1.edge_after !== undefined) {
        int_point2.edge_before.next = int_point1.edge_after;
        int_point1.edge_after.prev = int_point2.edge_before;
        int_point2.edge_after = int_point1.edge_after;
        int_point1.edge_before = int_point2.edge_before;
      }
    }
    if (int_point1.edge_before !== undefined && int_point1.edge_after === undefined) {
      for (let int_point of intersections.int_points1_sorted) {
        if (int_point === int_point1)
          continue;
        if (int_point.edge_before === undefined && int_point.edge_after !== undefined) {
          if (int_point.pt.equalTo(int_point1.pt)) {
            int_point1.edge_before.next = int_point.edge_after;
            int_point.edge_after.prev = int_point1.edge_before;
            int_point1.edge_after = int_point.edge_after;
            int_point.edge_before = int_point1.edge_before;
          }
        }
      }
    }
    if (int_point2.edge_before !== undefined && int_point2.edge_after === undefined) {
      for (let int_point of intersections.int_points2_sorted) {
        if (int_point === int_point2)
          continue;
        if (int_point.edge_before === undefined && int_point.edge_after !== undefined) {
          if (int_point.pt.equalTo(int_point2.pt)) {
            int_point2.edge_before.next = int_point.edge_after;
            int_point.edge_after.prev = int_point2.edge_before;
            int_point2.edge_after = int_point.edge_after;
            int_point.edge_before = int_point2.edge_before;
          }
        }
      }
    }
  }
}
function removeOldFaces(polygon, int_points) {
  for (let int_point of int_points) {
    polygon.faces.delete(int_point.face);
    int_point.face = undefined;
    if (int_point.edge_before)
      int_point.edge_before.face = undefined;
    if (int_point.edge_after)
      int_point.edge_after.face = undefined;
  }
}
function restoreFaces(polygon, int_points, other_int_points) {
  for (let int_point of int_points) {
    if (int_point.edge_before === undefined || int_point.edge_after === undefined)
      continue;
    if (int_point.face)
      continue;
    if (int_point.edge_after.face || int_point.edge_before.face)
      continue;
    let first = int_point.edge_after;
    let last = int_point.edge_before;
    try {
      LinkedList.testInfiniteLoop(first);
    } catch (error) {
      throw Errors.CANNOT_COMPLETE_BOOLEAN_OPERATION;
    }
    let face = polygon.addFace(first, last);
    for (let int_point_tmp of int_points) {
      if (int_point_tmp.edge_before && int_point_tmp.edge_after && int_point_tmp.edge_before.face === face && int_point_tmp.edge_after.face === face) {
        int_point_tmp.face = face;
      }
    }
    for (let int_point_tmp of other_int_points) {
      if (int_point_tmp.edge_before && int_point_tmp.edge_after && int_point_tmp.edge_before.face === face && int_point_tmp.edge_after.face === face) {
        int_point_tmp.face = face;
      }
    }
  }
}
function removeNotRelevantNotIntersectedFaces(polygon, notIntersectedFaces, op, is_res_polygon) {
  for (let face of notIntersectedFaces) {
    let rel = face.first.bv;
    if (op === BOOLEAN_UNION && rel === INSIDE$1 || op === BOOLEAN_SUBTRACT && rel === INSIDE$1 && is_res_polygon || op === BOOLEAN_SUBTRACT && rel === OUTSIDE && !is_res_polygon || op === BOOLEAN_INTERSECT && rel === OUTSIDE) {
      polygon.deleteFace(face);
    }
  }
}
function removeDetachedEdges(polygon) {
  const detachedEdges = [];
  for (const edge of polygon.edges) {
    if (!edge.face || !polygon.faces.has(edge.face)) {
      detachedEdges.push(edge);
    }
  }
  for (const edge of detachedEdges) {
    polygon.edges.delete(edge);
  }
}
var BooleanOperations = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  BOOLEAN_INTERSECT,
  BOOLEAN_SUBTRACT,
  BOOLEAN_UNION,
  calculateIntersections,
  innerClip,
  intersect: intersect$1,
  outerClip,
  removeNotRelevantChains,
  removeOldFaces,
  restoreFaces,
  subtract,
  unify
});
var EQUAL = RegExp("T.F..FFF.|T.F...F..");
var INTERSECT = RegExp("T........|.T.......|...T.....|....T....");
var TOUCH = RegExp("FT.......|F..T.....|F...T....");
var INSIDE = RegExp("T.F..F...");
var COVERED = RegExp("T.F..F...|.TF..F...|..FT.F...|..F.TF...");

class DE9IM {
  constructor() {
    this.m = new Array(9).fill(undefined);
  }
  get I2I() {
    return this.m[0];
  }
  set I2I(geom) {
    this.m[0] = geom;
  }
  get I2B() {
    return this.m[1];
  }
  set I2B(geom) {
    this.m[1] = geom;
  }
  get I2E() {
    return this.m[2];
  }
  set I2E(geom) {
    this.m[2] = geom;
  }
  get B2I() {
    return this.m[3];
  }
  set B2I(geom) {
    this.m[3] = geom;
  }
  get B2B() {
    return this.m[4];
  }
  set B2B(geom) {
    this.m[4] = geom;
  }
  get B2E() {
    return this.m[5];
  }
  set B2E(geom) {
    this.m[5] = geom;
  }
  get E2I() {
    return this.m[6];
  }
  set E2I(geom) {
    this.m[6] = geom;
  }
  get E2B() {
    return this.m[7];
  }
  set E2B(geom) {
    this.m[7] = geom;
  }
  get E2E() {
    return this.m[8];
  }
  set E2E(geom) {
    this.m[8] = geom;
  }
  toString() {
    return this.m.map((e) => {
      if (e instanceof Array && e.length > 0) {
        return "T";
      } else if (e instanceof Array && e.length === 0) {
        return "F";
      } else {
        return "*";
      }
    }).join("");
  }
  equal() {
    return EQUAL.test(this.toString());
  }
  intersect() {
    return INTERSECT.test(this.toString());
  }
  touch() {
    return TOUCH.test(this.toString());
  }
  inside() {
    return INSIDE.test(this.toString());
  }
  covered() {
    return COVERED.test(this.toString());
  }
}
function ray_shoot(polygon, point) {
  let contains = undefined;
  let ray = new Flatten.Ray(point);
  let line = new Flatten.Line(ray.pt, ray.norm);
  const searchBox = new Flatten.Box(ray.box.xmin - Flatten.DP_TOL, ray.box.ymin - Flatten.DP_TOL, ray.box.xmax + Flatten.DP_TOL, ray.box.ymax + Flatten.DP_TOL);
  if (polygon.box.not_intersect(searchBox)) {
    return Flatten.OUTSIDE;
  }
  let resp_edges = polygon.edges.search(searchBox);
  if (resp_edges.length === 0) {
    return Flatten.OUTSIDE;
  }
  for (let edge of resp_edges) {
    if (edge.shape.contains(point)) {
      return Flatten.BOUNDARY;
    }
  }
  let faces = [...polygon.faces];
  let intersections = [];
  for (let edge of resp_edges) {
    for (let ip of ray.intersect(edge.shape)) {
      if (ip.equalTo(point)) {
        return Flatten.BOUNDARY;
      }
      intersections.push({
        pt: ip,
        edge,
        face_index: faces.indexOf(edge.face)
      });
    }
  }
  intersections.sort((i1, i2) => {
    if (LT(i1.pt.x, i2.pt.x)) {
      return -1;
    }
    if (GT(i1.pt.x, i2.pt.x)) {
      return 1;
    }
    if (i1.face_index < i2.face_index) {
      return -1;
    }
    if (i1.face_index > i2.face_index) {
      return 1;
    }
    if (i1.edge.arc_length < i2.edge.arc_length) {
      return -1;
    }
    if (i1.edge.arc_length > i2.edge.arc_length) {
      return 1;
    }
    return 0;
  });
  let counter = 0;
  for (let i = 0;i < intersections.length; i++) {
    let intersection = intersections[i];
    if (intersection.pt.equalTo(intersection.edge.shape.start)) {
      if (i > 0 && intersection.pt.equalTo(intersections[i - 1].pt) && intersection.face_index === intersections[i - 1].face_index && intersection.edge.prev === intersections[i - 1].edge) {
        continue;
      }
      let prev_edge = intersection.edge.prev;
      while (EQ_0(prev_edge.length)) {
        prev_edge = prev_edge.prev;
      }
      let prev_tangent = prev_edge.shape.tangentInEnd();
      let prev_point = intersection.pt.translate(prev_tangent);
      let cur_tangent = intersection.edge.shape.tangentInStart();
      let cur_point = intersection.pt.translate(cur_tangent);
      let prev_on_the_left = prev_point.leftTo(line);
      let cur_on_the_left = cur_point.leftTo(line);
      if (prev_on_the_left && !cur_on_the_left || !prev_on_the_left && cur_on_the_left) {
        counter++;
      }
    } else if (intersection.pt.equalTo(intersection.edge.shape.end)) {
      if (i > 0 && intersection.pt.equalTo(intersections[i - 1].pt) && intersection.face_index === intersections[i - 1].face_index && intersection.edge.next === intersections[i - 1].edge) {
        continue;
      }
      let next_edge = intersection.edge.next;
      while (EQ_0(next_edge.length)) {
        next_edge = next_edge.next;
      }
      let next_tangent = next_edge.shape.tangentInStart();
      let next_point = intersection.pt.translate(next_tangent);
      let cur_tangent = intersection.edge.shape.tangentInEnd();
      let cur_point = intersection.pt.translate(cur_tangent);
      let next_on_the_left = next_point.leftTo(line);
      let cur_on_the_left = cur_point.leftTo(line);
      if (next_on_the_left && !cur_on_the_left || !next_on_the_left && cur_on_the_left) {
        counter++;
      }
    } else {
      if (intersection.edge.shape instanceof Flatten.Segment) {
        counter++;
      } else {
        let box = intersection.edge.shape.box;
        if (!(EQ(intersection.pt.y, box.ymin) || EQ(intersection.pt.y, box.ymax))) {
          counter++;
        }
      }
    }
  }
  contains = counter % 2 === 1 ? INSIDE$2 : OUTSIDE$1;
  return contains;
}
function equal(shape1, shape2) {
  return relate(shape1, shape2).equal();
}
function intersect(shape1, shape2) {
  return relate(shape1, shape2).intersect();
}
function touch(shape1, shape2) {
  return relate(shape1, shape2).touch();
}
function disjoint(shape1, shape2) {
  return !intersect(shape1, shape2);
}
function inside(shape1, shape2) {
  return relate(shape1, shape2).inside();
}
function covered(shape1, shape2) {
  return relate(shape1, shape2).covered();
}
function contain(shape1, shape2) {
  return inside(shape2, shape1);
}
function cover(shape1, shape2) {
  return covered(shape2, shape1);
}
function relate(shape1, shape2) {
  if (shape1 instanceof Flatten.Line && shape2 instanceof Flatten.Line) {
    return relateLine2Line(shape1, shape2);
  } else if (shape1 instanceof Flatten.Line && shape2 instanceof Flatten.Circle) {
    return relateLine2Circle(shape1, shape2);
  } else if (shape1 instanceof Flatten.Line && shape2 instanceof Flatten.Box) {
    return relateLine2Box(shape1, shape2);
  } else if (shape1 instanceof Flatten.Line && shape2 instanceof Flatten.Polygon) {
    return relateLine2Polygon(shape1, shape2);
  } else if ((shape1 instanceof Flatten.Segment || shape1 instanceof Flatten.Arc) && shape2 instanceof Flatten.Polygon) {
    return relateShape2Polygon(shape1, shape2);
  } else if ((shape1 instanceof Flatten.Segment || shape1 instanceof Flatten.Arc) && (shape2 instanceof Flatten.Circle || shape2 instanceof Flatten.Box)) {
    return relateShape2Polygon(shape1, new Flatten.Polygon(shape2));
  } else if (shape1 instanceof Flatten.Polygon && shape2 instanceof Flatten.Polygon) {
    return relatePolygon2Polygon(shape1, shape2);
  } else if ((shape1 instanceof Flatten.Circle || shape1 instanceof Flatten.Box) && (shape2 instanceof Flatten.Circle || shape2 instanceof Flatten.Box)) {
    return relatePolygon2Polygon(new Flatten.Polygon(shape1), new Flatten.Polygon(shape2));
  } else if ((shape1 instanceof Flatten.Circle || shape1 instanceof Flatten.Box) && shape2 instanceof Flatten.Polygon) {
    return relatePolygon2Polygon(new Flatten.Polygon(shape1), shape2);
  } else if (shape1 instanceof Flatten.Polygon && (shape2 instanceof Flatten.Circle || shape2 instanceof Flatten.Box)) {
    return relatePolygon2Polygon(shape1, new Flatten.Polygon(shape2));
  }
}
function relateLine2Line(line1, line2) {
  let denim = new DE9IM;
  let ip = intersectLine2Line(line1, line2);
  if (ip.length === 0) {
    if (line1.contains(line2.pt) && line2.contains(line1.pt)) {
      denim.I2I = [line1];
      denim.I2E = [];
      denim.E2I = [];
    } else {
      denim.I2I = [];
      denim.I2E = [line1];
      denim.E2I = [line2];
    }
  } else {
    denim.I2I = ip;
    denim.I2E = line1.split(ip);
    denim.E2I = line2.split(ip);
  }
  return denim;
}
function relateLine2Circle(line, circle) {
  let denim = new DE9IM;
  let ip = intersectLine2Circle(line, circle);
  if (ip.length === 0) {
    denim.I2I = [];
    denim.I2B = [];
    denim.I2E = [line];
    denim.E2I = [circle];
  } else if (ip.length === 1) {
    denim.I2I = [];
    denim.I2B = ip;
    denim.I2E = line.split(ip);
    denim.E2I = [circle];
  } else {
    let multiline = new Multiline$1([line]);
    let ip_sorted = line.sortPoints(ip);
    multiline.split(ip_sorted);
    let splitShapes = multiline.toShapes();
    denim.I2I = [splitShapes[1]];
    denim.I2B = ip_sorted;
    denim.I2E = [splitShapes[0], splitShapes[2]];
    denim.E2I = new Flatten.Polygon([circle.toArc()]).cutWithLine(line);
  }
  return denim;
}
function relateLine2Box(line, box) {
  let denim = new DE9IM;
  let ip = intersectLine2Box(line, box);
  if (ip.length === 0) {
    denim.I2I = [];
    denim.I2B = [];
    denim.I2E = [line];
    denim.E2I = [box];
  } else if (ip.length === 1) {
    denim.I2I = [];
    denim.I2B = ip;
    denim.I2E = line.split(ip);
    denim.E2I = [box];
  } else {
    let multiline = new Multiline$1([line]);
    let ip_sorted = line.sortPoints(ip);
    multiline.split(ip_sorted);
    let splitShapes = multiline.toShapes();
    if (box.toSegments().some((segment) => segment.contains(ip[0]) && segment.contains(ip[1]))) {
      denim.I2I = [];
      denim.I2B = [splitShapes[1]];
      denim.I2E = [splitShapes[0], splitShapes[2]];
      denim.E2I = [box];
    } else {
      denim.I2I = [splitShapes[1]];
      denim.I2B = ip_sorted;
      denim.I2E = [splitShapes[0], splitShapes[2]];
      denim.E2I = new Flatten.Polygon(box.toSegments()).cutWithLine(line);
    }
  }
  return denim;
}
function relateLine2Polygon(line, polygon) {
  let denim = new DE9IM;
  let ip = intersectLine2Polygon(line, polygon);
  let multiline = new Multiline$1([line]);
  let ip_sorted = ip.length > 0 ? ip.slice() : line.sortPoints(ip);
  multiline.split(ip_sorted);
  [...multiline].forEach((edge) => edge.setInclusion(polygon));
  denim.I2I = [...multiline].filter((edge) => edge.bv === Flatten.INSIDE).map((edge) => edge.shape);
  denim.I2B = [...multiline].slice(1).map((edge) => edge.bv === Flatten.BOUNDARY ? edge.shape : edge.shape.start);
  denim.I2E = [...multiline].filter((edge) => edge.bv === Flatten.OUTSIDE).map((edge) => edge.shape);
  denim.E2I = polygon.cutWithLine(line);
  return denim;
}
function relateShape2Polygon(shape, polygon) {
  let denim = new DE9IM;
  let ip = intersectShape2Polygon(shape, polygon);
  let ip_sorted = ip.length > 0 ? ip.slice() : shape.sortPoints(ip);
  let multiline = new Multiline$1([shape]);
  multiline.split(ip_sorted);
  [...multiline].forEach((edge) => edge.setInclusion(polygon));
  denim.I2I = [...multiline].filter((edge) => edge.bv === Flatten.INSIDE).map((edge) => edge.shape);
  denim.I2B = [...multiline].slice(1).map((edge) => edge.bv === Flatten.BOUNDARY ? edge.shape : edge.shape.start);
  denim.I2E = [...multiline].filter((edge) => edge.bv === Flatten.OUTSIDE).map((edge) => edge.shape);
  denim.B2I = [];
  denim.B2B = [];
  denim.B2E = [];
  for (let pt of [shape.start, shape.end]) {
    switch (ray_shoot(polygon, pt)) {
      case Flatten.INSIDE:
        denim.B2I.push(pt);
        break;
      case Flatten.BOUNDARY:
        denim.B2B.push(pt);
        break;
      case Flatten.OUTSIDE:
        denim.B2E.push(pt);
        break;
    }
  }
  return denim;
}
function relatePolygon2Polygon(polygon1, polygon2) {
  let denim = new DE9IM;
  let [ip_sorted1, ip_sorted2] = calculateIntersections(polygon1, polygon2);
  let boolean_intersection = intersect$1(polygon1, polygon2);
  let boolean_difference1 = subtract(polygon1, polygon2);
  let boolean_difference2 = subtract(polygon2, polygon1);
  let [inner_clip_shapes1, inner_clip_shapes2] = innerClip(polygon1, polygon2);
  let outer_clip_shapes1 = outerClip(polygon1, polygon2);
  let outer_clip_shapes2 = outerClip(polygon2, polygon1);
  denim.I2I = boolean_intersection.isEmpty() ? [] : [boolean_intersection];
  denim.I2B = inner_clip_shapes2;
  denim.I2E = boolean_difference1.isEmpty() ? [] : [boolean_difference1];
  denim.B2I = inner_clip_shapes1;
  denim.B2B = ip_sorted1;
  denim.B2E = outer_clip_shapes1;
  denim.E2I = boolean_difference2.isEmpty() ? [] : [boolean_difference2];
  denim.E2B = outer_clip_shapes2;
  return denim;
}
var Relations = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  contain,
  cover,
  covered,
  disjoint,
  equal,
  inside,
  intersect,
  relate,
  touch
});

class Matrix {
  constructor(a = 1, b = 0, c = 0, d = 1, tx = 0, ty = 0) {
    this.a = a;
    this.b = b;
    this.c = c;
    this.d = d;
    this.tx = tx;
    this.ty = ty;
  }
  fromMatrix3x3(matrix3x3) {
    const [a, c, tx] = matrix3x3[0];
    const [b, d, ty] = matrix3x3[1];
    return new Matrix(a, b, c, d, tx, ty);
  }
  toMatrix3x3() {
    return [
      [this.a, this.c, this.tx],
      [this.b, this.d, this.ty],
      [0, 0, 1]
    ];
  }
  clone() {
    return new Matrix(this.a, this.b, this.c, this.d, this.tx, this.ty);
  }
  transform(vector) {
    return [
      vector[0] * this.a + vector[1] * this.c + this.tx,
      vector[0] * this.b + vector[1] * this.d + this.ty
    ];
  }
  multiply(other_matrix) {
    return new Matrix(this.a * other_matrix.a + this.c * other_matrix.b, this.b * other_matrix.a + this.d * other_matrix.b, this.a * other_matrix.c + this.c * other_matrix.d, this.b * other_matrix.c + this.d * other_matrix.d, this.a * other_matrix.tx + this.c * other_matrix.ty + this.tx, this.b * other_matrix.tx + this.d * other_matrix.ty + this.ty);
  }
  translate(...args) {
    let tx, ty;
    if (args.length == 1 && !isNaN(args[0].x) && !isNaN(args[0].y)) {
      tx = args[0].x;
      ty = args[0].y;
    } else if (args.length === 2 && typeof args[0] == "number" && typeof args[1] == "number") {
      tx = args[0];
      ty = args[1];
    } else {
      throw Errors.ILLEGAL_PARAMETERS;
    }
    return this.multiply(new Matrix(1, 0, 0, 1, tx, ty));
  }
  rotate(angle, centerX = 0, centerY = 0) {
    let cos = Math.cos(angle);
    let sin = Math.sin(angle);
    return this.translate(centerX, centerY).multiply(new Matrix(cos, sin, -sin, cos, 0, 0)).translate(-centerX, -centerY);
  }
  scale(sx, sy) {
    return this.multiply(new Matrix(sx, 0, 0, sy, 0, 0));
  }
  equalTo(matrix) {
    if (!Flatten.Utils.EQ(this.tx, matrix.tx))
      return false;
    if (!Flatten.Utils.EQ(this.ty, matrix.ty))
      return false;
    if (!Flatten.Utils.EQ(this.a, matrix.a))
      return false;
    if (!Flatten.Utils.EQ(this.b, matrix.b))
      return false;
    if (!Flatten.Utils.EQ(this.c, matrix.c))
      return false;
    if (!Flatten.Utils.EQ(this.d, matrix.d))
      return false;
    return true;
  }
}
Flatten.Matrix = Matrix;
var matrix = (...args) => new Flatten.Matrix(...args);
Flatten.matrix = matrix;

class IntervalBase {
  constructor(low, high) {
    this.low = low;
    this.high = high;
  }
  get max() {
    return this.clone();
  }
  less_than(other_interval) {
    return this.low < other_interval.low || this.low === other_interval.low && this.high < other_interval.high;
  }
  equal_to(other_interval) {
    return this.low === other_interval.low && this.high === other_interval.high;
  }
  intersect(other_interval) {
    return !this.not_intersect(other_interval);
  }
  not_intersect(other_interval) {
    return this.high < other_interval.low || other_interval.high < this.low;
  }
  merge(other_interval) {
    const low = this.low === undefined ? other_interval.low : this.low < other_interval.low ? this.low : other_interval.low;
    const high = this.high === undefined ? other_interval.high : this.high > other_interval.high ? this.high : other_interval.high;
    const cloned = this.clone();
    cloned.low = low;
    cloned.high = high;
    return cloned;
  }
  output() {
    return [this.low, this.high];
  }
  comparable_less_than(val1, val2) {
    return val1 < val2;
  }
}

class Interval extends IntervalBase {
  clone() {
    return new Interval(this.low, this.high);
  }
}
var RB_TREE_COLOR_RED = 1;
var RB_TREE_COLOR_BLACK = 0;

class Node {
  constructor(key, value, left = null, right = null, parent = null, color = RB_TREE_COLOR_BLACK) {
    this.left = left;
    this.right = right;
    this.parent = parent;
    this.color = color;
    this.item = { key: undefined, values: [] };
    if (value !== undefined) {
      this.item.values.push(value);
    }
    if (key !== undefined) {
      if (Array.isArray(key)) {
        const [rawLow, rawHigh] = key;
        if (!Number.isNaN(rawLow) && !Number.isNaN(rawHigh)) {
          let low = rawLow;
          let high = rawHigh;
          if (low > high)
            [low, high] = [high, low];
          this.item.key = new Interval(low, high);
        }
      } else {
        this.item.key = key;
      }
    }
    this.max = this.item.key ? this.item.key.max : undefined;
  }
  isNil() {
    return this.item.key === undefined && this.item.values.length === 0 && this.left === null && this.right === null && this.color === RB_TREE_COLOR_BLACK;
  }
  requireKey() {
    if (!this.item.key) {
      throw new Error("Node key is undefined (nil/sentinel). Operation is not applicable.");
    }
    return this.item.key;
  }
  less_than(other_node) {
    const a = this.requireKey();
    const b = other_node.requireKey();
    return a.less_than(b);
  }
  _value_equal(other_node) {
    const a = this.item.values[0];
    const b = other_node.item.values[0];
    return a && b && a.equal_to ? a.equal_to(b) : a === b;
  }
  equal_to(other_node) {
    const a = this.requireKey();
    const b = other_node.requireKey();
    return a.equal_to(b);
  }
  intersect(other_node) {
    const a = this.requireKey();
    const b = other_node.requireKey();
    return a.intersect(b);
  }
  copy_data(other_node) {
    this.item.key = other_node.item.key;
    this.item.values = other_node.item.values.slice();
  }
  update_max() {
    this.max = this.item.key ? this.item.key.max : undefined;
    if (this.right && this.right.max) {
      this.max = this.max ? this.max.merge(this.right.max) : this.right.max;
    }
    if (this.left && this.left.max) {
      this.max = this.max ? this.max.merge(this.left.max) : this.left.max;
    }
  }
  not_intersect_left_subtree(search_node) {
    if (!this.left)
      return true;
    const high = this.left.max ? this.left.max.high : this.left.item.key.high;
    const selfKey = this.requireKey();
    const searchKey = search_node.requireKey();
    return selfKey.comparable_less_than(high, searchKey.low);
  }
  not_intersect_right_subtree(search_node) {
    if (!this.right)
      return true;
    const low = this.right.max ? this.right.max.low : this.right.item.key.low;
    const selfKey = this.requireKey();
    const searchKey = search_node.requireKey();
    return selfKey.comparable_less_than(searchKey.high, low);
  }
}

class IntervalTree {
  constructor() {
    this.root = null;
    this.nil_node = new Node;
  }
  get size() {
    let count = 0;
    this.tree_walk(this.root, (node) => count += node.item.values.length);
    return count;
  }
  get keys() {
    const res = [];
    this.tree_walk(this.root, (node) => res.push(node.item.key.output()));
    return res;
  }
  get values() {
    const res = [];
    this.tree_walk(this.root, (node) => {
      for (const v of node.item.values)
        res.push(v);
    });
    return res;
  }
  get items() {
    const res = [];
    this.tree_walk(this.root, (node) => {
      const keyOut = node.item.key.output();
      for (const v of node.item.values) {
        res.push({ key: keyOut, value: v });
      }
    });
    return res;
  }
  isEmpty() {
    return this.root == null || this.root === this.nil_node;
  }
  clear() {
    this.root = null;
  }
  insert(key, value = key) {
    if (key === undefined)
      return;
    const existing = this.tree_search(this.root, new Node(key));
    if (existing) {
      existing.item.values.push(value);
      return existing;
    }
    const insert_node = new Node(key, value, this.nil_node, this.nil_node, null, RB_TREE_COLOR_RED);
    this.tree_insert(insert_node);
    this.recalc_max(insert_node);
    return insert_node;
  }
  exist(key, value = key) {
    const node = this.tree_search(this.root, new Node(key));
    if (!node)
      return false;
    if (arguments.length < 2 || value === key)
      return true;
    return node.item.values.some((v) => v && v.equal_to ? v.equal_to(value) : v === value);
  }
  remove(key, value = key) {
    const node = this.tree_search(this.root, new Node(key));
    if (!node)
      return;
    if (arguments.length < 2) {
      this.tree_delete(node);
      return node;
    }
    const idx = node.item.values.findIndex((v) => v && v.equal_to ? v.equal_to(value) : v === value);
    if (idx >= 0) {
      node.item.values.splice(idx, 1);
      if (node.item.values.length === 0) {
        this.tree_delete(node);
      }
      return node;
    }
    return;
  }
  search(interval, outputMapperFn = (value, key) => value === key ? key.output() : value) {
    const search_node = new Node(interval);
    const resp_nodes = [];
    this.tree_search_interval(this.root, search_node, resp_nodes);
    const res = [];
    for (const node of resp_nodes) {
      for (const v of node.item.values) {
        res.push(outputMapperFn(v, node.item.key));
      }
    }
    return res;
  }
  intersect_any(interval) {
    const search_node = new Node(interval);
    return this.tree_find_any_interval(this.root, search_node);
  }
  forEach(visitor) {
    this.tree_walk(this.root, (node) => {
      for (const v of node.item.values)
        visitor(node.item.key, v);
    });
  }
  map(callback) {
    const tree = new IntervalTree;
    this.tree_walk(this.root, (node) => {
      for (const v of node.item.values) {
        tree.insert(node.item.key, callback(v, node.item.key));
      }
    });
    return tree;
  }
  *iterate(interval, outputMapperFn = (value, key) => value === key ? key.output() : value) {
    let node = null;
    if (interval) {
      node = this.tree_search_nearest_forward(this.root, new Node(interval));
    } else if (this.root) {
      node = this.local_minimum(this.root);
    }
    while (node) {
      for (const v of node.item.values) {
        yield outputMapperFn(v, node.item.key);
      }
      node = this.tree_successor(node);
    }
  }
  recalc_max(node) {
    let node_current = node;
    while (node_current.parent != null) {
      node_current.parent.update_max();
      node_current = node_current.parent;
    }
  }
  tree_insert(insert_node) {
    let current_node = this.root;
    let parent_node = null;
    if (this.root == null || this.root === this.nil_node) {
      this.root = insert_node;
    } else {
      while (current_node !== this.nil_node) {
        parent_node = current_node;
        if (insert_node.less_than(current_node)) {
          current_node = current_node.left;
        } else {
          current_node = current_node.right;
        }
      }
      insert_node.parent = parent_node;
      if (insert_node.less_than(parent_node)) {
        parent_node.left = insert_node;
      } else {
        parent_node.right = insert_node;
      }
    }
    this.insert_fixup(insert_node);
  }
  insert_fixup(insert_node) {
    let current_node;
    let uncle_node;
    current_node = insert_node;
    while (current_node !== this.root && current_node.parent.color === RB_TREE_COLOR_RED) {
      if (current_node.parent === current_node.parent.parent.left) {
        uncle_node = current_node.parent.parent.right;
        if (uncle_node.color === RB_TREE_COLOR_RED) {
          current_node.parent.color = RB_TREE_COLOR_BLACK;
          uncle_node.color = RB_TREE_COLOR_BLACK;
          current_node.parent.parent.color = RB_TREE_COLOR_RED;
          current_node = current_node.parent.parent;
        } else {
          if (current_node === current_node.parent.right) {
            current_node = current_node.parent;
            this.rotate_left(current_node);
          }
          current_node.parent.color = RB_TREE_COLOR_BLACK;
          current_node.parent.parent.color = RB_TREE_COLOR_RED;
          this.rotate_right(current_node.parent.parent);
        }
      } else {
        uncle_node = current_node.parent.parent.left;
        if (uncle_node.color === RB_TREE_COLOR_RED) {
          current_node.parent.color = RB_TREE_COLOR_BLACK;
          uncle_node.color = RB_TREE_COLOR_BLACK;
          current_node.parent.parent.color = RB_TREE_COLOR_RED;
          current_node = current_node.parent.parent;
        } else {
          if (current_node === current_node.parent.left) {
            current_node = current_node.parent;
            this.rotate_right(current_node);
          }
          current_node.parent.color = RB_TREE_COLOR_BLACK;
          current_node.parent.parent.color = RB_TREE_COLOR_RED;
          this.rotate_left(current_node.parent.parent);
        }
      }
    }
    this.root.color = RB_TREE_COLOR_BLACK;
  }
  tree_delete(delete_node) {
    let cut_node;
    let fix_node;
    if (delete_node.left === this.nil_node || delete_node.right === this.nil_node) {
      cut_node = delete_node;
    } else {
      cut_node = this.tree_successor(delete_node);
    }
    if (cut_node.left !== this.nil_node) {
      fix_node = cut_node.left;
    } else {
      fix_node = cut_node.right;
    }
    fix_node.parent = cut_node.parent;
    if (cut_node === this.root) {
      this.root = fix_node;
    } else {
      if (cut_node === cut_node.parent.left) {
        cut_node.parent.left = fix_node;
      } else {
        cut_node.parent.right = fix_node;
      }
      cut_node.parent.update_max();
    }
    this.recalc_max(fix_node);
    if (cut_node !== delete_node) {
      delete_node.copy_data(cut_node);
      delete_node.update_max();
      this.recalc_max(delete_node);
    }
    if (cut_node.color === RB_TREE_COLOR_BLACK) {
      this.delete_fixup(fix_node);
    }
  }
  delete_fixup(fix_node) {
    let current_node = fix_node;
    let brother_node;
    while (current_node !== this.root && current_node.parent != null && current_node.color === RB_TREE_COLOR_BLACK) {
      if (current_node === current_node.parent.left) {
        brother_node = current_node.parent.right;
        if (brother_node.color === RB_TREE_COLOR_RED) {
          brother_node.color = RB_TREE_COLOR_BLACK;
          current_node.parent.color = RB_TREE_COLOR_RED;
          this.rotate_left(current_node.parent);
          brother_node = current_node.parent.right;
        }
        if (brother_node.left.color === RB_TREE_COLOR_BLACK && brother_node.right.color === RB_TREE_COLOR_BLACK) {
          brother_node.color = RB_TREE_COLOR_RED;
          current_node = current_node.parent;
        } else {
          if (brother_node.right.color === RB_TREE_COLOR_BLACK) {
            brother_node.color = RB_TREE_COLOR_RED;
            brother_node.left.color = RB_TREE_COLOR_BLACK;
            this.rotate_right(brother_node);
            brother_node = current_node.parent.right;
          }
          brother_node.color = current_node.parent.color;
          current_node.parent.color = RB_TREE_COLOR_BLACK;
          brother_node.right.color = RB_TREE_COLOR_BLACK;
          this.rotate_left(current_node.parent);
          current_node = this.root;
        }
      } else {
        brother_node = current_node.parent.left;
        if (brother_node.color === RB_TREE_COLOR_RED) {
          brother_node.color = RB_TREE_COLOR_BLACK;
          current_node.parent.color = RB_TREE_COLOR_RED;
          this.rotate_right(current_node.parent);
          brother_node = current_node.parent.left;
        }
        if (brother_node.left.color === RB_TREE_COLOR_BLACK && brother_node.right.color === RB_TREE_COLOR_BLACK) {
          brother_node.color = RB_TREE_COLOR_RED;
          current_node = current_node.parent;
        } else {
          if (brother_node.left.color === RB_TREE_COLOR_BLACK) {
            brother_node.color = RB_TREE_COLOR_RED;
            brother_node.right.color = RB_TREE_COLOR_BLACK;
            this.rotate_left(brother_node);
            brother_node = current_node.parent.left;
          }
          brother_node.color = current_node.parent.color;
          current_node.parent.color = RB_TREE_COLOR_BLACK;
          brother_node.left.color = RB_TREE_COLOR_BLACK;
          this.rotate_right(current_node.parent);
          current_node = this.root;
        }
      }
    }
    current_node.color = RB_TREE_COLOR_BLACK;
  }
  tree_search(node, search_node) {
    if (node == null || node === this.nil_node)
      return;
    if (search_node.equal_to(node)) {
      return node;
    }
    if (search_node.less_than(node)) {
      return this.tree_search(node.left, search_node);
    } else {
      return this.tree_search(node.right, search_node);
    }
  }
  tree_search_nearest_forward(node, search_node) {
    let best = null;
    let curr = node;
    while (curr && curr !== this.nil_node) {
      if (curr.less_than(search_node)) {
        if (curr.intersect(search_node)) {
          best = curr;
          curr = curr.left;
        } else {
          curr = curr.right;
        }
      } else {
        if (!best || curr.less_than(best))
          best = curr;
        curr = curr.left;
      }
    }
    return best || null;
  }
  tree_search_interval(node, search_node, res) {
    if (node != null && node !== this.nil_node) {
      if (node.left !== this.nil_node && !node.not_intersect_left_subtree(search_node)) {
        this.tree_search_interval(node.left, search_node, res);
      }
      if (node.intersect(search_node)) {
        res.push(node);
      }
      if (node.right !== this.nil_node && !node.not_intersect_right_subtree(search_node)) {
        this.tree_search_interval(node.right, search_node, res);
      }
    }
  }
  tree_find_any_interval(node, search_node) {
    let found = false;
    if (node != null && node !== this.nil_node) {
      if (node.left !== this.nil_node && !node.not_intersect_left_subtree(search_node)) {
        found = this.tree_find_any_interval(node.left, search_node);
      }
      if (!found) {
        found = node.intersect(search_node);
      }
      if (!found && node.right !== this.nil_node && !node.not_intersect_right_subtree(search_node)) {
        found = this.tree_find_any_interval(node.right, search_node);
      }
    }
    return found;
  }
  local_minimum(node) {
    let node_min = node;
    while (node_min.left != null && node_min.left !== this.nil_node) {
      node_min = node_min.left;
    }
    return node_min;
  }
  local_maximum(node) {
    let node_max = node;
    while (node_max.right != null && node_max.right !== this.nil_node) {
      node_max = node_max.right;
    }
    return node_max;
  }
  tree_successor(node) {
    let node_successor;
    let current_node;
    let parent_node;
    if (node.right !== this.nil_node) {
      node_successor = this.local_minimum(node.right);
    } else {
      current_node = node;
      parent_node = node.parent;
      while (parent_node != null && parent_node.right === current_node) {
        current_node = parent_node;
        parent_node = parent_node.parent;
      }
      node_successor = parent_node;
    }
    return node_successor;
  }
  rotate_left(x) {
    const y = x.right;
    x.right = y.left;
    if (y.left !== this.nil_node) {
      y.left.parent = x;
    }
    y.parent = x.parent;
    if (x === this.root) {
      this.root = y;
    } else {
      if (x === x.parent.left) {
        x.parent.left = y;
      } else {
        x.parent.right = y;
      }
    }
    y.left = x;
    x.parent = y;
    if (x !== null && x !== this.nil_node) {
      x.update_max();
    }
    if (y != null && y !== this.nil_node) {
      y.update_max();
    }
  }
  rotate_right(y) {
    const x = y.left;
    y.left = x.right;
    if (x.right !== this.nil_node) {
      x.right.parent = y;
    }
    x.parent = y.parent;
    if (y === this.root) {
      this.root = x;
    } else {
      if (y === y.parent.left) {
        y.parent.left = x;
      } else {
        y.parent.right = x;
      }
    }
    x.right = y;
    y.parent = x;
    if (y !== null && y !== this.nil_node) {
      y.update_max();
    }
    if (x != null && x !== this.nil_node) {
      x.update_max();
    }
  }
  tree_walk(node, action) {
    if (node != null && node !== this.nil_node) {
      this.tree_walk(node.left, action);
      action(node);
      this.tree_walk(node.right, action);
    }
  }
  testRedBlackProperty() {
    let res = true;
    this.tree_walk(this.root, function(node) {
      if (node.color === RB_TREE_COLOR_RED) {
        if (!(node.left.color === RB_TREE_COLOR_BLACK && node.right.color === RB_TREE_COLOR_BLACK)) {
          res = false;
        }
      }
    });
    return res;
  }
  testBlackHeightProperty(node) {
    let height = 0;
    let heightLeft = 0;
    let heightRight = 0;
    if (node.color === RB_TREE_COLOR_BLACK) {
      height++;
    }
    if (node.left !== this.nil_node) {
      heightLeft = this.testBlackHeightProperty(node.left);
    } else {
      heightLeft = 1;
    }
    if (node.right !== this.nil_node) {
      heightRight = this.testBlackHeightProperty(node.right);
    } else {
      heightRight = 1;
    }
    if (heightLeft !== heightRight) {
      throw new Error("Red-black height property violated");
    }
    height += heightLeft;
    return height;
  }
}

class PlanarSet extends Set {
  constructor(shapes) {
    super(shapes);
    this.index = new IntervalTree;
    this.forEach((shape) => this.index.insert(shape));
  }
  add(entry) {
    let size = this.size;
    const { key, value } = entry;
    const box = key || entry.box;
    const shape = value || entry;
    super.add(shape);
    if (this.size > size) {
      this.index.insert(box, shape);
    }
    return this;
  }
  delete(entry) {
    const { key, value } = entry;
    const box = key || entry.box;
    const shape = value || entry;
    let deleted = super.delete(shape);
    if (deleted) {
      this.index.remove(box, shape);
    }
    return deleted;
  }
  clear() {
    super.clear();
    this.index = new IntervalTree;
  }
  search(box) {
    let resp = this.index.search(box);
    return resp;
  }
  hit(point) {
    let box = new Flatten.Box(point.x - 1, point.y - 1, point.x + 1, point.y + 1);
    let resp = this.index.search(box);
    return resp.filter((shape) => point.on(shape));
  }
  svg() {
    let svgcontent = [...this].reduce((acc, shape) => acc + shape.svg(), "");
    return svgcontent;
  }
}
Flatten.PlanarSet = PlanarSet;

class Shape {
  get name() {
    throw Errors.CANNOT_INVOKE_ABSTRACT_METHOD;
  }
  get box() {
    throw Errors.CANNOT_INVOKE_ABSTRACT_METHOD;
  }
  clone() {
    throw Errors.CANNOT_INVOKE_ABSTRACT_METHOD;
  }
  translate(...args) {
    return this.transform(new Matrix().translate(...args));
  }
  rotate(angle, center = new Flatten.Point) {
    return this.transform(new Matrix().rotate(angle, center.x, center.y));
  }
  scale(sx, sy) {
    return this.transform(new Matrix().scale(sx, sy));
  }
  transform(...args) {
    throw Errors.CANNOT_INVOKE_ABSTRACT_METHOD;
  }
  toJSON() {
    return Object.assign({}, this, { name: this.name });
  }
  svg(attrs = {}) {
    throw Errors.CANNOT_INVOKE_ABSTRACT_METHOD;
  }
}
var Point$2 = class Point extends Shape {
  constructor(...args) {
    super();
    this.x = 0;
    this.y = 0;
    if (args.length === 0) {
      return;
    }
    if (args.length === 1 && args[0] instanceof Array && args[0].length === 2) {
      let arr = args[0];
      if (typeof arr[0] == "number" && typeof arr[1] == "number") {
        this.x = arr[0];
        this.y = arr[1];
        return;
      }
    }
    if (args.length === 1 && args[0] instanceof Object && args[0].name === "point") {
      let { x, y } = args[0];
      this.x = x;
      this.y = y;
      return;
    }
    if (args.length === 2) {
      if (typeof args[0] == "number" && typeof args[1] == "number") {
        this.x = args[0];
        this.y = args[1];
        return;
      }
    }
    throw Errors.ILLEGAL_PARAMETERS;
  }
  get box() {
    return new Flatten.Box(this.x, this.y, this.x, this.y);
  }
  clone() {
    return new Flatten.Point(this.x, this.y);
  }
  get vertices() {
    return [this.clone()];
  }
  equalTo(pt) {
    return Flatten.Utils.EQ(this.x, pt.x) && Flatten.Utils.EQ(this.y, pt.y);
  }
  lessThan(pt) {
    if (Flatten.Utils.LT(this.y, pt.y))
      return true;
    if (Flatten.Utils.EQ(this.y, pt.y) && Flatten.Utils.LT(this.x, pt.x))
      return true;
    return false;
  }
  transform(m) {
    return new Flatten.Point(m.transform([this.x, this.y]));
  }
  projectionOn(line) {
    if (this.equalTo(line.pt))
      return this.clone();
    let vec = new Flatten.Vector(this, line.pt);
    if (Flatten.Utils.EQ_0(vec.cross(line.norm)))
      return line.pt.clone();
    let dist = vec.dot(line.norm);
    let proj_vec = line.norm.multiply(dist);
    return this.translate(proj_vec);
  }
  leftTo(line) {
    let vec = new Flatten.Vector(line.pt, this);
    let onLeftSemiPlane = Flatten.Utils.GT(vec.dot(line.norm), 0);
    return onLeftSemiPlane;
  }
  distanceTo(shape) {
    if (shape instanceof Point) {
      let dx = shape.x - this.x;
      let dy = shape.y - this.y;
      return [Math.sqrt(dx * dx + dy * dy), new Flatten.Segment(this, shape)];
    }
    if (shape instanceof Flatten.Line) {
      return Flatten.Distance.point2line(this, shape);
    }
    if (shape instanceof Flatten.Circle) {
      return Flatten.Distance.point2circle(this, shape);
    }
    if (shape instanceof Flatten.Segment) {
      return Flatten.Distance.point2segment(this, shape);
    }
    if (shape instanceof Flatten.Arc) {
      return Flatten.Distance.point2arc(this, shape);
    }
    if (shape instanceof Flatten.Box) {
      return Flatten.Distance.point2polygon(this, new Flatten.Polygon(shape));
    }
    if (shape instanceof Flatten.Polygon) {
      return Flatten.Distance.point2polygon(this, shape);
    }
    if (shape instanceof Flatten.PlanarSet) {
      return Flatten.Distance.shape2planarSet(this, shape);
    }
    if (shape instanceof Flatten.Multiline) {
      return Flatten.Distance.shape2multiline(this, shape);
    }
  }
  on(shape) {
    if (shape instanceof Flatten.Point) {
      return this.equalTo(shape);
    }
    if (shape.contains && shape.contains instanceof Function) {
      return shape.contains(this);
    }
    throw Flatten.Errors.UNSUPPORTED_SHAPE_TYPE;
  }
  get name() {
    return "point";
  }
  svg(attrs = {}) {
    const r = attrs.r ?? 3;
    return `
<circle cx="${this.x}" cy="${this.y}" r="${r}"
            ${convertToString({ fill: "red", ...attrs })} />`;
  }
};
Flatten.Point = Point$2;
var point2 = (...args) => new Flatten.Point(...args);
Flatten.point = point2;
var Vector$1 = class Vector extends Shape {
  constructor(...args) {
    super();
    this.x = 0;
    this.y = 0;
    if (args.length === 0) {
      return;
    }
    if (args.length === 1 && args[0] instanceof Array && args[0].length === 2) {
      let arr = args[0];
      if (typeof arr[0] == "number" && typeof arr[1] == "number") {
        this.x = arr[0];
        this.y = arr[1];
        return;
      }
    }
    if (args.length === 1 && args[0] instanceof Object && args[0].name === "vector") {
      let { x, y } = args[0];
      this.x = x;
      this.y = y;
      return;
    }
    if (args.length === 1 && args[0] instanceof Object && args[0].name === "segment") {
      let { start, end } = args[0];
      this.x = end.x - start.x;
      this.y = end.y - start.y;
      return;
    }
    if (args.length === 2) {
      let a1 = args[0];
      let a2 = args[1];
      if (typeof a1 == "number" && typeof a2 == "number") {
        this.x = a1;
        this.y = a2;
        return;
      }
      if (a1 instanceof Flatten.Point && a2 instanceof Flatten.Point) {
        this.x = a2.x - a1.x;
        this.y = a2.y - a1.y;
        return;
      }
    }
    throw Errors.ILLEGAL_PARAMETERS;
  }
  clone() {
    return new Flatten.Vector(this.x, this.y);
  }
  get slope() {
    let angle = Math.atan2(this.y, this.x);
    if (angle < 0)
      angle = 2 * Math.PI + angle;
    return angle;
  }
  get length() {
    return Math.sqrt(this.dot(this));
  }
  isZeroLength() {
    return Flatten.Utils.EQ_0(this.length);
  }
  equalTo(v) {
    return Flatten.Utils.EQ(this.x, v.x) && Flatten.Utils.EQ(this.y, v.y);
  }
  multiply(scalar) {
    return new Flatten.Vector(scalar * this.x, scalar * this.y);
  }
  dot(v) {
    return this.x * v.x + this.y * v.y;
  }
  cross(v) {
    return this.x * v.y - this.y * v.x;
  }
  normalize() {
    if (this.isZeroLength()) {
      throw Errors.ZERO_DIVISION;
    }
    return new Flatten.Vector(this.x / this.length, this.y / this.length);
  }
  rotate(angle, center = new Flatten.Point) {
    if (center.x === 0 && center.y === 0) {
      return this.transform(new Matrix().rotate(angle));
    }
    throw Errors.OPERATION_IS_NOT_SUPPORTED;
  }
  transform(m) {
    return new Flatten.Vector(m.transform([this.x, this.y]));
  }
  rotate90CCW() {
    return new Flatten.Vector(-this.y, this.x);
  }
  rotate90CW() {
    return new Flatten.Vector(this.y, -this.x);
  }
  invert() {
    return new Flatten.Vector(-this.x, -this.y);
  }
  add(v) {
    return new Flatten.Vector(this.x + v.x, this.y + v.y);
  }
  subtract(v) {
    return new Flatten.Vector(this.x - v.x, this.y - v.y);
  }
  angleTo(v) {
    let norm1 = this.normalize();
    let norm2 = v.normalize();
    let angle = Math.atan2(norm1.cross(norm2), norm1.dot(norm2));
    if (angle < 0)
      angle += 2 * Math.PI;
    return angle;
  }
  projectionOn(v) {
    let n = v.normalize();
    let d = this.dot(n);
    return n.multiply(d);
  }
  get name() {
    return "vector";
  }
};
Flatten.Vector = Vector$1;
var vector$1 = (...args) => new Flatten.Vector(...args);
Flatten.vector = vector$1;
var Segment$1 = class Segment extends Shape {
  constructor(...args) {
    super();
    this.ps = new Flatten.Point;
    this.pe = new Flatten.Point;
    if (args.length === 0) {
      return;
    }
    if (args.length === 1 && args[0] instanceof Array && args[0].length === 4) {
      let coords = args[0];
      this.ps = new Flatten.Point(coords[0], coords[1]);
      this.pe = new Flatten.Point(coords[2], coords[3]);
      return;
    }
    if (args.length === 1 && args[0] instanceof Object && args[0].name === "segment") {
      let { ps, pe } = args[0];
      this.ps = new Flatten.Point(ps.x, ps.y);
      this.pe = new Flatten.Point(pe.x, pe.y);
      return;
    }
    if (args.length === 1 && args[0] instanceof Flatten.Point) {
      this.ps = args[0].clone();
      return;
    }
    if (args.length === 2 && args[0] instanceof Flatten.Point && args[1] instanceof Flatten.Point) {
      this.ps = args[0].clone();
      this.pe = args[1].clone();
      return;
    }
    if (args.length === 4) {
      this.ps = new Flatten.Point(args[0], args[1]);
      this.pe = new Flatten.Point(args[2], args[3]);
      return;
    }
    throw Errors.ILLEGAL_PARAMETERS;
  }
  clone() {
    return new Flatten.Segment(this.start, this.end);
  }
  get start() {
    return this.ps;
  }
  get end() {
    return this.pe;
  }
  get vertices() {
    return [this.ps.clone(), this.pe.clone()];
  }
  get length() {
    return this.start.distanceTo(this.end)[0];
  }
  get slope() {
    let vec = new Flatten.Vector(this.start, this.end);
    return vec.slope;
  }
  get box() {
    return new Flatten.Box(Math.min(this.start.x, this.end.x), Math.min(this.start.y, this.end.y), Math.max(this.start.x, this.end.x), Math.max(this.start.y, this.end.y));
  }
  equalTo(seg) {
    return this.ps.equalTo(seg.ps) && this.pe.equalTo(seg.pe);
  }
  contains(pt) {
    return Flatten.Utils.EQ_0(this.distanceToPoint(pt));
  }
  intersect(shape) {
    if (shape instanceof Flatten.Point) {
      return this.contains(shape) ? [shape] : [];
    }
    if (shape instanceof Flatten.Line) {
      return intersectSegment2Line(this, shape);
    }
    if (shape instanceof Flatten.Ray) {
      return intersectRay2Segment(shape, this);
    }
    if (shape instanceof Flatten.Segment) {
      return intersectSegment2Segment(this, shape);
    }
    if (shape instanceof Flatten.Circle) {
      return intersectSegment2Circle(this, shape);
    }
    if (shape instanceof Flatten.Box) {
      return intersectSegment2Box(this, shape);
    }
    if (shape instanceof Flatten.Arc) {
      return intersectSegment2Arc(this, shape);
    }
    if (shape instanceof Flatten.Polygon) {
      return intersectSegment2Polygon(this, shape);
    }
    if (shape instanceof Flatten.Multiline) {
      return intersectShape2Multiline(this, shape);
    }
  }
  distanceTo(shape) {
    if (shape instanceof Flatten.Point) {
      let [dist, shortest_segment] = Flatten.Distance.point2segment(shape, this);
      shortest_segment = shortest_segment.reverse();
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Circle) {
      let [dist, shortest_segment] = Flatten.Distance.segment2circle(this, shape);
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Line) {
      let [dist, shortest_segment] = Flatten.Distance.segment2line(this, shape);
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Segment) {
      let [dist, shortest_segment] = Flatten.Distance.segment2segment(this, shape);
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Arc) {
      let [dist, shortest_segment] = Flatten.Distance.segment2arc(this, shape);
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Box) {
      let [dist, shortest_segment] = Flatten.Distance.shape2polygon(this, new Flatten.Polygon(shape));
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Polygon) {
      let [dist, shortest_segment] = Flatten.Distance.shape2polygon(this, shape);
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.PlanarSet) {
      let [dist, shortest_segment] = Flatten.Distance.shape2planarSet(this, shape);
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Multiline) {
      return Flatten.Distance.shape2multiline(this, shape);
    }
  }
  tangentInStart() {
    let vec = new Flatten.Vector(this.start, this.end);
    return vec.normalize();
  }
  tangentInEnd() {
    let vec = new Flatten.Vector(this.end, this.start);
    return vec.normalize();
  }
  reverse() {
    return new Segment(this.end, this.start);
  }
  split(pt) {
    if (this.start.equalTo(pt))
      return [null, this.clone()];
    if (this.end.equalTo(pt))
      return [this.clone(), null];
    return [
      new Flatten.Segment(this.start, pt),
      new Flatten.Segment(pt, this.end)
    ];
  }
  middle() {
    return new Flatten.Point((this.start.x + this.end.x) / 2, (this.start.y + this.end.y) / 2);
  }
  pointAtLength(length) {
    if (length > this.length || length < 0)
      return null;
    if (length == 0)
      return this.start;
    if (length == this.length)
      return this.end;
    let factor = length / this.length;
    return new Flatten.Point((this.end.x - this.start.x) * factor + this.start.x, (this.end.y - this.start.y) * factor + this.start.y);
  }
  distanceToPoint(pt) {
    let [dist, ...rest] = Flatten.Distance.point2segment(pt, this);
    return dist;
  }
  definiteIntegral(ymin = 0) {
    let dx = this.end.x - this.start.x;
    let dy1 = this.start.y - ymin;
    let dy2 = this.end.y - ymin;
    return dx * (dy1 + dy2) / 2;
  }
  transform(matrix = new Flatten.Matrix) {
    return new Segment(this.ps.transform(matrix), this.pe.transform(matrix));
  }
  isZeroLength() {
    return this.ps.equalTo(this.pe);
  }
  sortPoints(pts) {
    let line = new Flatten.Line(this.start, this.end);
    return line.sortPoints(pts);
  }
  get name() {
    return "segment";
  }
  svg(attrs = {}) {
    return `
<line x1="${this.start.x}" y1="${this.start.y}" x2="${this.end.x}" y2="${this.end.y}" ${convertToString(attrs)} />`;
  }
};
Flatten.Segment = Segment$1;
var segment = (...args) => new Flatten.Segment(...args);
Flatten.segment = segment;
var { vector } = Flatten;
var Line$1 = class Line extends Shape {
  constructor(...args) {
    super();
    this.pt = new Flatten.Point;
    this.norm = new Flatten.Vector(0, 1);
    if (args.length === 0) {
      return;
    }
    if (args.length === 1 && args[0] instanceof Object && args[0].name === "line") {
      let { pt, norm } = args[0];
      this.pt = new Flatten.Point(pt);
      this.norm = new Flatten.Vector(norm);
      return;
    }
    if (args.length === 2) {
      let a1 = args[0];
      let a2 = args[1];
      if (a1 instanceof Flatten.Point && a2 instanceof Flatten.Point) {
        this.pt = a1;
        this.norm = Line.points2norm(a1, a2);
        if (this.norm.dot(vector(this.pt.x, this.pt.y)) >= 0) {
          this.norm.invert();
        }
        return;
      }
      if (a1 instanceof Flatten.Point && a2 instanceof Flatten.Vector) {
        if (Flatten.Utils.EQ_0(a2.x) && Flatten.Utils.EQ_0(a2.y)) {
          throw Errors.ILLEGAL_PARAMETERS;
        }
        this.pt = a1.clone();
        this.norm = a2.clone();
        this.norm = this.norm.normalize();
        if (this.norm.dot(vector(this.pt.x, this.pt.y)) >= 0) {
          this.norm.invert();
        }
        return;
      }
      if (a1 instanceof Flatten.Vector && a2 instanceof Flatten.Point) {
        if (Flatten.Utils.EQ_0(a1.x) && Flatten.Utils.EQ_0(a1.y)) {
          throw Errors.ILLEGAL_PARAMETERS;
        }
        this.pt = a2.clone();
        this.norm = a1.clone();
        this.norm = this.norm.normalize();
        if (this.norm.dot(vector(this.pt.x, this.pt.y)) >= 0) {
          this.norm.invert();
        }
        return;
      }
    }
    throw Errors.ILLEGAL_PARAMETERS;
  }
  clone() {
    return new Flatten.Line(this.pt, this.norm);
  }
  get start() {
    return;
  }
  get end() {
    return;
  }
  get length() {
    return Number.POSITIVE_INFINITY;
  }
  get box() {
    return new Flatten.Box(Number.NEGATIVE_INFINITY, Number.NEGATIVE_INFINITY, Number.POSITIVE_INFINITY, Number.POSITIVE_INFINITY);
  }
  get middle() {
    return;
  }
  get slope() {
    let vec = new Flatten.Vector(this.norm.y, -this.norm.x);
    return vec.slope;
  }
  get standard() {
    let A = this.norm.x;
    let B = this.norm.y;
    let C = this.norm.dot(vector(this.pt.x, this.pt.y));
    return [A, B, C];
  }
  parallelTo(other_line) {
    return Flatten.Utils.EQ_0(this.norm.cross(other_line.norm));
  }
  incidentTo(other_line) {
    return this.parallelTo(other_line) && this.pt.on(other_line);
  }
  contains(pt) {
    if (this.pt.equalTo(pt)) {
      return true;
    }
    let vec = new Flatten.Vector(this.pt, pt);
    return Flatten.Utils.EQ_0(this.norm.dot(vec));
  }
  coord(pt) {
    return vector(pt.x, pt.y).cross(this.norm);
  }
  intersect(shape) {
    if (shape instanceof Flatten.Point) {
      return this.contains(shape) ? [shape] : [];
    }
    if (shape instanceof Flatten.Line) {
      return intersectLine2Line(this, shape);
    }
    if (shape instanceof Flatten.Ray) {
      return intersectRay2Line(shape, this);
    }
    if (shape instanceof Flatten.Circle) {
      return intersectLine2Circle(this, shape);
    }
    if (shape instanceof Flatten.Box) {
      return intersectLine2Box(this, shape);
    }
    if (shape instanceof Flatten.Segment) {
      return intersectSegment2Line(shape, this);
    }
    if (shape instanceof Flatten.Arc) {
      return intersectLine2Arc(this, shape);
    }
    if (shape instanceof Flatten.Polygon) {
      return intersectLine2Polygon(this, shape);
    }
    if (shape instanceof Flatten.Multiline) {
      return intersectShape2Multiline(this, shape);
    }
  }
  distanceTo(shape) {
    if (shape instanceof Flatten.Point) {
      let [distance, shortest_segment] = Flatten.Distance.point2line(shape, this);
      shortest_segment = shortest_segment.reverse();
      return [distance, shortest_segment];
    }
    if (shape instanceof Flatten.Circle) {
      let [distance, shortest_segment] = Flatten.Distance.circle2line(shape, this);
      shortest_segment = shortest_segment.reverse();
      return [distance, shortest_segment];
    }
    if (shape instanceof Flatten.Segment) {
      let [distance, shortest_segment] = Flatten.Distance.segment2line(shape, this);
      return [distance, shortest_segment.reverse()];
    }
    if (shape instanceof Flatten.Arc) {
      let [distance, shortest_segment] = Flatten.Distance.arc2line(shape, this);
      return [distance, shortest_segment.reverse()];
    }
    if (shape instanceof Flatten.Box) {
      let [distance, shortest_segment] = Flatten.Distance.shape2polygon(this, new Flatten.Polygon(shape));
      return [distance, shortest_segment];
    }
    if (shape instanceof Flatten.Polygon) {
      let [distance, shortest_segment] = Flatten.Distance.shape2polygon(this, shape);
      return [distance, shortest_segment];
    }
  }
  split(pt) {
    if (pt instanceof Flatten.Point) {
      return [new Flatten.Ray(pt, this.norm), new Flatten.Ray(pt, this.norm)];
    } else {
      let multiline = new Flatten.Multiline([this]);
      let sorted_points = this.sortPoints(pt);
      multiline.split(sorted_points);
      return multiline.toShapes();
    }
  }
  rotate(angle, center = new Flatten.Point) {
    return new Flatten.Line(this.pt.rotate(angle, center), this.norm.rotate(angle));
  }
  transform(m) {
    return new Flatten.Line(this.pt.transform(m), this.norm.clone());
  }
  sortPoints(pts) {
    return pts.slice().sort((pt1, pt2) => {
      if (this.coord(pt1) < this.coord(pt2)) {
        return -1;
      }
      if (this.coord(pt1) > this.coord(pt2)) {
        return 1;
      }
      return 0;
    });
  }
  get name() {
    return "line";
  }
  svg(box, attrs = {}) {
    let ip = intersectLine2Box(this, box);
    if (ip.length === 0)
      return "";
    let ps = ip[0];
    let pe = ip.length === 2 ? ip[1] : ip.find((pt) => !pt.equalTo(ps));
    if (pe === undefined)
      pe = ps;
    let segment = new Flatten.Segment(ps, pe);
    return segment.svg(attrs);
  }
  static points2norm(pt1, pt2) {
    if (pt1.equalTo(pt2)) {
      throw Errors.ILLEGAL_PARAMETERS;
    }
    let vec = new Flatten.Vector(pt1, pt2);
    let unit = vec.normalize();
    return unit.rotate90CCW();
  }
};
Flatten.Line = Line$1;
var line = (...args) => new Flatten.Line(...args);
Flatten.line = line;
var Circle$1 = class Circle extends Shape {
  constructor(...args) {
    super();
    this.pc = new Flatten.Point;
    this.r = 1;
    if (args.length === 1 && args[0] instanceof Object && args[0].name === "circle") {
      let { pc, r } = args[0];
      this.pc = new Flatten.Point(pc);
      this.r = r;
    } else {
      let [pc, r] = [...args];
      if (pc && pc instanceof Flatten.Point)
        this.pc = pc.clone();
      if (r !== undefined)
        this.r = r;
    }
  }
  clone() {
    return new Flatten.Circle(this.pc.clone(), this.r);
  }
  get center() {
    return this.pc;
  }
  get box() {
    return new Flatten.Box(this.pc.x - this.r, this.pc.y - this.r, this.pc.x + this.r, this.pc.y + this.r);
  }
  contains(shape) {
    if (shape instanceof Flatten.Point) {
      return Flatten.Utils.LE(shape.distanceTo(this.center)[0], this.r);
    }
    if (shape instanceof Flatten.Segment) {
      return Flatten.Utils.LE(shape.start.distanceTo(this.center)[0], this.r) && Flatten.Utils.LE(shape.end.distanceTo(this.center)[0], this.r);
    }
    if (shape instanceof Flatten.Arc) {
      return this.intersect(shape).length === 0 && Flatten.Utils.LE(shape.start.distanceTo(this.center)[0], this.r) && Flatten.Utils.LE(shape.end.distanceTo(this.center)[0], this.r);
    }
    if (shape instanceof Flatten.Circle) {
      return this.intersect(shape).length === 0 && Flatten.Utils.LE(shape.r, this.r) && Flatten.Utils.LE(shape.center.distanceTo(this.center)[0], this.r);
    }
  }
  toArc(counterclockwise = true) {
    return new Flatten.Arc(this.center, this.r, Math.PI, -Math.PI, counterclockwise);
  }
  scale(sx, sy) {
    if (sx !== sy)
      throw Errors.OPERATION_IS_NOT_SUPPORTED;
    if (!(this.pc.x === 0 && this.pc.y === 0))
      throw Errors.OPERATION_IS_NOT_SUPPORTED;
    return new Flatten.Circle(this.pc, this.r * sx);
  }
  transform(matrix = new Flatten.Matrix) {
    return new Flatten.Circle(this.pc.transform(matrix), this.r);
  }
  intersect(shape) {
    if (shape instanceof Flatten.Point) {
      return this.contains(shape) ? [shape] : [];
    }
    if (shape instanceof Flatten.Line) {
      return intersectLine2Circle(shape, this);
    }
    if (shape instanceof Flatten.Ray) {
      return intersectRay2Circle(shape, this);
    }
    if (shape instanceof Flatten.Segment) {
      return intersectSegment2Circle(shape, this);
    }
    if (shape instanceof Flatten.Circle) {
      return intersectCircle2Circle(shape, this);
    }
    if (shape instanceof Flatten.Box) {
      return intersectCircle2Box(this, shape);
    }
    if (shape instanceof Flatten.Arc) {
      return intersectArc2Circle(shape, this);
    }
    if (shape instanceof Flatten.Polygon) {
      return intersectCircle2Polygon(this, shape);
    }
    if (shape instanceof Flatten.Multiline) {
      return intersectShape2Multiline(this, shape);
    }
  }
  distanceTo(shape) {
    if (shape instanceof Flatten.Point) {
      let [distance, shortest_segment] = Flatten.Distance.point2circle(shape, this);
      shortest_segment = shortest_segment.reverse();
      return [distance, shortest_segment];
    }
    if (shape instanceof Flatten.Circle) {
      let [distance, shortest_segment] = Flatten.Distance.circle2circle(this, shape);
      return [distance, shortest_segment];
    }
    if (shape instanceof Flatten.Line) {
      let [distance, shortest_segment] = Flatten.Distance.circle2line(this, shape);
      return [distance, shortest_segment];
    }
    if (shape instanceof Flatten.Segment) {
      let [distance, shortest_segment] = Flatten.Distance.segment2circle(shape, this);
      shortest_segment = shortest_segment.reverse();
      return [distance, shortest_segment];
    }
    if (shape instanceof Flatten.Arc) {
      let [distance, shortest_segment] = Flatten.Distance.arc2circle(shape, this);
      shortest_segment = shortest_segment.reverse();
      return [distance, shortest_segment];
    }
    if (shape instanceof Flatten.Box) {
      let [distance, shortest_segment] = Flatten.Distance.shape2polygon(this, new Flatten.Polygon(shape));
      return [distance, shortest_segment];
    }
    if (shape instanceof Flatten.Polygon) {
      let [distance, shortest_segment] = Flatten.Distance.shape2polygon(this, shape);
      return [distance, shortest_segment];
    }
    if (shape instanceof Flatten.PlanarSet) {
      let [dist, shortest_segment] = Flatten.Distance.shape2planarSet(this, shape);
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Multiline) {
      let [dist, shortest_segment] = Flatten.Distance.shape2multiline(this, shape);
      return [dist, shortest_segment];
    }
  }
  get name() {
    return "circle";
  }
  svg(attrs = {}) {
    return `
<circle cx="${this.pc.x}" cy="${this.pc.y}" r="${this.r}"
                ${convertToString({ fill: "none", ...attrs })} />`;
  }
};
Flatten.Circle = Circle$1;
var circle = (...args) => new Flatten.Circle(...args);
Flatten.circle = circle;

class Arc extends Shape {
  constructor(...args) {
    super();
    this.pc = new Flatten.Point;
    this.r = 1;
    this.startAngle = 0;
    this.endAngle = 2 * Math.PI;
    this.counterClockwise = true;
    if (args.length === 0)
      return;
    if (args.length === 1 && args[0] instanceof Object && args[0].name === "arc") {
      let { pc, r, startAngle, endAngle, counterClockwise } = args[0];
      this.pc = new Flatten.Point(pc.x, pc.y);
      this.r = r;
      this.startAngle = startAngle;
      this.endAngle = endAngle;
      this.counterClockwise = counterClockwise;
    } else {
      let [pc, r, startAngle, endAngle, counterClockwise] = [...args];
      if (pc && pc instanceof Flatten.Point)
        this.pc = pc.clone();
      if (r !== undefined)
        this.r = r;
      if (startAngle !== undefined)
        this.startAngle = startAngle;
      if (endAngle !== undefined)
        this.endAngle = endAngle;
      if (counterClockwise !== undefined)
        this.counterClockwise = counterClockwise;
    }
  }
  clone() {
    return new Flatten.Arc(this.pc.clone(), this.r, this.startAngle, this.endAngle, this.counterClockwise);
  }
  get sweep() {
    let startAngle = this.startAngle;
    let endAngle = this.endAngle;
    if (Flatten.Utils.EQ(Math.abs(startAngle - endAngle), Flatten.PIx2)) {
      return Flatten.PIx2;
    }
    if (Math.abs(startAngle) > Flatten.PIx2) {
      startAngle -= Math.trunc(startAngle / Flatten.PIx2) * Flatten.PIx2;
    }
    if (startAngle < 0) {
      startAngle += Flatten.PIx2;
    }
    if (Math.abs(endAngle) > Flatten.PIx2) {
      endAngle -= Math.trunc(endAngle / Flatten.PIx2) * Flatten.PIx2;
    }
    if (endAngle < 0) {
      endAngle += Flatten.PIx2;
    }
    let sweep = this.counterClockwise ? endAngle - startAngle : startAngle - endAngle;
    if (sweep < 0) {
      sweep += Flatten.PIx2;
    }
    return sweep;
  }
  get start() {
    let p0 = new Flatten.Point(this.pc.x + this.r, this.pc.y);
    return p0.rotate(this.startAngle, this.pc);
  }
  get end() {
    let p0 = new Flatten.Point(this.pc.x + this.r, this.pc.y);
    return p0.rotate(this.endAngle, this.pc);
  }
  get center() {
    return this.pc.clone();
  }
  get vertices() {
    return [this.start.clone(), this.end.clone()];
  }
  get length() {
    return Math.abs(this.sweep * this.r);
  }
  get box() {
    let func_arcs = this.breakToFunctional();
    let box = func_arcs.reduce((acc, arc) => acc.merge(arc.start.box), new Flatten.Box);
    box = box.merge(this.end.box);
    return box;
  }
  contains(pt) {
    if (!Flatten.Utils.EQ(this.pc.distanceTo(pt)[0], this.r))
      return false;
    if (pt.equalTo(this.start))
      return true;
    let angle = new Flatten.Vector(this.pc, pt).slope;
    let test_arc = new Flatten.Arc(this.pc, this.r, this.startAngle, angle, this.counterClockwise);
    return Flatten.Utils.LE(test_arc.length, this.length);
  }
  split(pt) {
    if (this.start.equalTo(pt))
      return [null, this.clone()];
    if (this.end.equalTo(pt))
      return [this.clone(), null];
    let angle = new Flatten.Vector(this.pc, pt).slope;
    return [
      new Flatten.Arc(this.pc, this.r, this.startAngle, angle, this.counterClockwise),
      new Flatten.Arc(this.pc, this.r, angle, this.endAngle, this.counterClockwise)
    ];
  }
  middle() {
    let endAngle = this.counterClockwise ? this.startAngle + this.sweep / 2 : this.startAngle - this.sweep / 2;
    let arc = new Flatten.Arc(this.pc, this.r, this.startAngle, endAngle, this.counterClockwise);
    return arc.end;
  }
  pointAtLength(length) {
    if (length > this.length || length < 0)
      return null;
    if (length === 0)
      return this.start;
    if (length === this.length)
      return this.end;
    let factor = length / this.length;
    let endAngle = this.counterClockwise ? this.startAngle + this.sweep * factor : this.startAngle - this.sweep * factor;
    let arc = new Flatten.Arc(this.pc, this.r, this.startAngle, endAngle, this.counterClockwise);
    return arc.end;
  }
  chordHeight() {
    return (1 - Math.cos(Math.abs(this.sweep / 2))) * this.r;
  }
  intersect(shape) {
    if (shape instanceof Flatten.Point) {
      return this.contains(shape) ? [shape] : [];
    }
    if (shape instanceof Flatten.Line) {
      return intersectLine2Arc(shape, this);
    }
    if (shape instanceof Flatten.Ray) {
      return intersectRay2Arc(shape, this);
    }
    if (shape instanceof Flatten.Circle) {
      return intersectArc2Circle(this, shape);
    }
    if (shape instanceof Flatten.Segment) {
      return intersectSegment2Arc(shape, this);
    }
    if (shape instanceof Flatten.Box) {
      return intersectArc2Box(this, shape);
    }
    if (shape instanceof Flatten.Arc) {
      return intersectArc2Arc(this, shape);
    }
    if (shape instanceof Flatten.Polygon) {
      return intersectArc2Polygon(this, shape);
    }
    if (shape instanceof Flatten.Multiline) {
      return intersectShape2Multiline(this, shape);
    }
  }
  distanceTo(shape) {
    if (shape instanceof Flatten.Point) {
      let [dist, shortest_segment] = Flatten.Distance.point2arc(shape, this);
      shortest_segment = shortest_segment.reverse();
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Circle) {
      let [dist, shortest_segment] = Flatten.Distance.arc2circle(this, shape);
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Line) {
      let [dist, shortest_segment] = Flatten.Distance.arc2line(this, shape);
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Segment) {
      let [dist, shortest_segment] = Flatten.Distance.segment2arc(shape, this);
      shortest_segment = shortest_segment.reverse();
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Arc) {
      let [dist, shortest_segment] = Flatten.Distance.arc2arc(this, shape);
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Box) {
      let [dist, shortest_segment] = Flatten.Distance.shape2polygon(this, new Flatten.Polygon(shape));
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Polygon) {
      let [dist, shortest_segment] = Flatten.Distance.shape2polygon(this, shape);
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.PlanarSet) {
      let [dist, shortest_segment] = Flatten.Distance.shape2planarSet(this, shape);
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Multiline) {
      return Flatten.Distance.shape2multiline(this, shape);
    }
  }
  breakToFunctional() {
    let func_arcs_array = [];
    let angles = [0, Math.PI / 2, Math.PI, 3 * Math.PI / 2];
    let startAngle = this.startAngle;
    let endAngle = this.endAngle;
    if (Flatten.Utils.EQ(Math.abs(startAngle - endAngle), Flatten.PIx2)) {
      endAngle = startAngle;
    }
    if (Math.abs(startAngle) > Flatten.PIx2) {
      startAngle -= Math.trunc(startAngle / Flatten.PIx2) * Flatten.PIx2;
    }
    if (startAngle < 0) {
      startAngle += Flatten.PIx2;
    }
    if (Math.abs(endAngle) > Flatten.PIx2) {
      endAngle -= Math.trunc(endAngle / Flatten.PIx2) * Flatten.PIx2;
    }
    if (endAngle < 0) {
      endAngle += Flatten.PIx2;
    }
    let prev = startAngle;
    let next;
    let firstj;
    let d;
    if (this.counterClockwise) {
      firstj = Math.ceil(startAngle / (Math.PI / 2)) % 4;
      d = 1;
    } else {
      firstj = Math.floor(startAngle / (Math.PI / 2)) % 4;
      d = -1;
    }
    for (let i = 0, j = firstj;i < 4; i++, j = (j + d + 4) % 4) {
      next = angles[j];
      if (next === prev) {
        continue;
      }
      let incrementalSweep = this.counterClockwise ? next - startAngle : startAngle - next;
      if (incrementalSweep < 0) {
        incrementalSweep += Flatten.PIx2;
      }
      if (incrementalSweep > this.sweep) {
        break;
      }
      func_arcs_array.push(new Flatten.Arc(this.pc, this.r, prev, next, this.counterClockwise));
      prev = next;
    }
    if (func_arcs_array.length === 0) {
      func_arcs_array.push(this);
      return func_arcs_array;
    }
    next = endAngle;
    if (prev !== next) {
      func_arcs_array.push(new Flatten.Arc(this.pc, this.r, prev, next, this.counterClockwise));
    }
    return func_arcs_array;
  }
  tangentInStart() {
    let vec = new Flatten.Vector(this.pc, this.start);
    let angle = this.counterClockwise ? Math.PI / 2 : -Math.PI / 2;
    return vec.rotate(angle).normalize();
  }
  tangentInEnd() {
    let vec = new Flatten.Vector(this.pc, this.end);
    let angle = this.counterClockwise ? -Math.PI / 2 : Math.PI / 2;
    return vec.rotate(angle).normalize();
  }
  reverse() {
    return new Flatten.Arc(this.pc, this.r, this.endAngle, this.startAngle, !this.counterClockwise);
  }
  transform(matrix = new Flatten.Matrix) {
    let newStart = this.start.transform(matrix);
    let newEnd = this.end.transform(matrix);
    let newCenter = this.pc.transform(matrix);
    let newDirection = this.counterClockwise;
    if (matrix.a * matrix.d < 0) {
      newDirection = !newDirection;
    }
    return Flatten.Arc.arcSE(newCenter, newStart, newEnd, newDirection);
  }
  static arcSE(center, start, end, counterClockwise) {
    let { vector } = Flatten;
    let startAngle = vector(center, start).slope;
    let endAngle = vector(center, end).slope;
    if (Flatten.Utils.EQ(startAngle, endAngle)) {
      endAngle += 2 * Math.PI;
      counterClockwise = true;
    }
    let r = vector(center, start).length;
    return new Flatten.Arc(center, r, startAngle, endAngle, counterClockwise);
  }
  definiteIntegral(ymin = 0) {
    let f_arcs = this.breakToFunctional();
    let area = f_arcs.reduce((acc, arc) => acc + arc.circularSegmentDefiniteIntegral(ymin), 0);
    return area;
  }
  circularSegmentDefiniteIntegral(ymin) {
    let segment = new Flatten.Segment(this.start, this.end);
    let areaTrapez = segment.definiteIntegral(ymin);
    let areaCircularSegment = Flatten.Utils.EQ(this.sweep, Flatten.PIx2) ? 0 : this.circularSegmentArea();
    return this.counterClockwise ? areaTrapez - areaCircularSegment : areaTrapez + areaCircularSegment;
  }
  circularSegmentArea() {
    return 0.5 * this.r * this.r * (this.sweep - Math.sin(this.sweep));
  }
  sortPoints(pts) {
    let { vector } = Flatten;
    return pts.slice().sort((pt1, pt2) => {
      let slope1 = vector(this.pc, pt1).slope;
      let slope2 = vector(this.pc, pt2).slope;
      if (slope1 < slope2) {
        return -1;
      }
      if (slope1 > slope2) {
        return 1;
      }
      return 0;
    });
  }
  get name() {
    return "arc";
  }
  svg(attrs = {}) {
    let largeArcFlag = this.sweep <= Math.PI ? "0" : "1";
    let sweepFlag = this.counterClockwise ? "1" : "0";
    if (Flatten.Utils.EQ(this.sweep, 2 * Math.PI)) {
      let circle = new Flatten.Circle(this.pc, this.r);
      return circle.svg(attrs);
    } else {
      return `
<path d="M${this.start.x},${this.start.y}
                             A${this.r},${this.r} 0 ${largeArcFlag},${sweepFlag} ${this.end.x},${this.end.y}"
                    ${convertToString({ fill: "none", ...attrs })} />`;
    }
  }
}
Flatten.Arc = Arc;
var arc = (...args) => new Flatten.Arc(...args);
Flatten.arc = arc;

class Box extends Shape {
  constructor(xmin = undefined, ymin = undefined, xmax = undefined, ymax = undefined) {
    super();
    this.xmin = xmin;
    this.ymin = ymin;
    this.xmax = xmax;
    this.ymax = ymax;
  }
  clone() {
    return new Box(this.xmin, this.ymin, this.xmax, this.ymax);
  }
  get low() {
    return new Flatten.Point(this.xmin, this.ymin);
  }
  get high() {
    return new Flatten.Point(this.xmax, this.ymax);
  }
  get max() {
    return this.clone();
  }
  get center() {
    return new Flatten.Point((this.xmin + this.xmax) / 2, (this.ymin + this.ymax) / 2);
  }
  get width() {
    return Math.abs(this.xmax - this.xmin);
  }
  get height() {
    return Math.abs(this.ymax - this.ymin);
  }
  get box() {
    return this.clone();
  }
  not_intersect(other_box) {
    return this.xmax < other_box.xmin || this.xmin > other_box.xmax || this.ymax < other_box.ymin || this.ymin > other_box.ymax;
  }
  intersect(other_box) {
    return !this.not_intersect(other_box);
  }
  merge(other_box) {
    return new Box(this.xmin === undefined ? other_box.xmin : Math.min(this.xmin, other_box.xmin), this.ymin === undefined ? other_box.ymin : Math.min(this.ymin, other_box.ymin), this.xmax === undefined ? other_box.xmax : Math.max(this.xmax, other_box.xmax), this.ymax === undefined ? other_box.ymax : Math.max(this.ymax, other_box.ymax));
  }
  less_than(other_box) {
    if (this.low.lessThan(other_box.low))
      return true;
    if (this.low.equalTo(other_box.low) && this.high.lessThan(other_box.high))
      return true;
    return false;
  }
  equal_to(other_box) {
    return this.low.equalTo(other_box.low) && this.high.equalTo(other_box.high);
  }
  output() {
    return this.clone();
  }
  comparable_less_than(pt1, pt2) {
    return pt1.lessThan(pt2);
  }
  set(xmin, ymin, xmax, ymax) {
    this.xmin = xmin;
    this.ymin = ymin;
    this.xmax = xmax;
    this.ymax = ymax;
  }
  extend(extension) {
    if (extension <= 0)
      return this.clone();
    return new Box(this.xmin - extension, this.ymin - extension, this.xmax + extension, this.ymax + extension);
  }
  toPoints() {
    return [
      new Flatten.Point(this.xmin, this.ymin),
      new Flatten.Point(this.xmax, this.ymin),
      new Flatten.Point(this.xmax, this.ymax),
      new Flatten.Point(this.xmin, this.ymax)
    ];
  }
  toSegments() {
    let pts = this.toPoints();
    return [
      new Flatten.Segment(pts[0], pts[1]),
      new Flatten.Segment(pts[1], pts[2]),
      new Flatten.Segment(pts[2], pts[3]),
      new Flatten.Segment(pts[3], pts[0])
    ];
  }
  rotate(angle, center = new Flatten.Point) {
    throw Errors.OPERATION_IS_NOT_SUPPORTED;
  }
  transform(m = new Flatten.Matrix) {
    const transformed_points = this.toPoints().map((pt) => pt.transform(m));
    return transformed_points.reduce((new_box, pt) => new_box.merge(pt.box), new Box);
  }
  contains(shape) {
    if (shape instanceof Flatten.Point) {
      return shape.x >= this.xmin && shape.x <= this.xmax && shape.y >= this.ymin && shape.y <= this.ymax;
    }
    if (shape instanceof Flatten.Segment) {
      return shape.vertices.every((vertex) => this.contains(vertex));
    }
    if (shape instanceof Flatten.Box) {
      return shape.toSegments().every((segment) => this.contains(segment));
    }
    if (shape instanceof Flatten.Circle) {
      return this.contains(shape.box);
    }
    if (shape instanceof Flatten.Arc) {
      return shape.vertices.every((vertex) => this.contains(vertex)) && this.toSegments().every((segment) => intersectSegment2Arc(segment, shape).length === 0);
    }
    if (shape instanceof Flatten.Line || shape instanceof Flatten.Ray) {
      return false;
    }
    if (shape instanceof Flatten.Multiline) {
      return shape.toShapes().every((shape) => this.contains(shape));
    }
    if (shape instanceof Flatten.Polygon) {
      return this.contains(shape.box);
    }
  }
  distanceTo(shape) {
    const distanceInfos = this.toSegments().map((segment) => segment.distanceTo(shape));
    let shortestDistanceInfo = [
      Number.MAX_SAFE_INTEGER,
      null
    ];
    distanceInfos.forEach((distanceInfo) => {
      if (distanceInfo[0] < shortestDistanceInfo[0]) {
        shortestDistanceInfo = distanceInfo;
      }
    });
    return shortestDistanceInfo;
  }
  get name() {
    return "box";
  }
  svg(attrs = {}) {
    const width = this.xmax - this.xmin;
    const height = this.ymax - this.ymin;
    return `
<rect x="${this.xmin}" y="${this.ymin}" width="${width}" height="${height}"
                ${convertToString({ fill: "none", ...attrs })} />`;
  }
}
Flatten.Box = Box;
var box = (...args) => new Flatten.Box(...args);
Flatten.box = box;

class Edge {
  constructor(shape) {
    this.shape = shape;
    this.next = undefined;
    this.prev = undefined;
    this.face = undefined;
    this.arc_length = 0;
    this.bvStart = undefined;
    this.bvEnd = undefined;
    this.bv = undefined;
    this.overlap = undefined;
  }
  get start() {
    return this.shape.start;
  }
  get end() {
    return this.shape.end;
  }
  get length() {
    return this.shape.length;
  }
  get box() {
    return this.shape.box;
  }
  get isSegment() {
    return this.shape instanceof Flatten.Segment;
  }
  get isArc() {
    return this.shape instanceof Flatten.Arc;
  }
  get isLine() {
    return this.shape instanceof Flatten.Line;
  }
  get isRay() {
    return this.shape instanceof Flatten.Ray;
  }
  middle() {
    return this.shape.middle();
  }
  pointAtLength(length) {
    return this.shape.pointAtLength(length);
  }
  contains(pt) {
    return this.shape.contains(pt);
  }
  setInclusion(polygon) {
    if (this.bv !== undefined)
      return this.bv;
    if (this.shape instanceof Flatten.Line || this.shape instanceof Flatten.Ray) {
      this.bv = Flatten.OUTSIDE;
      return this.bv;
    }
    if (this.bvStart === undefined) {
      this.bvStart = ray_shoot(polygon, this.start);
    }
    if (this.bvEnd === undefined) {
      this.bvEnd = ray_shoot(polygon, this.end);
    }
    if (this.bvStart === Flatten.OUTSIDE || this.bvEnd == Flatten.OUTSIDE) {
      this.bv = Flatten.OUTSIDE;
    } else if (this.bvStart === Flatten.INSIDE || this.bvEnd == Flatten.INSIDE) {
      this.bv = Flatten.INSIDE;
    } else {
      let bvMiddle = ray_shoot(polygon, this.middle());
      this.bv = bvMiddle;
    }
    return this.bv;
  }
  setOverlap(edge) {
    let flag = undefined;
    let shape1 = this.shape;
    let shape2 = edge.shape;
    if (shape1 instanceof Flatten.Segment && shape2 instanceof Flatten.Segment) {
      if (shape1.start.equalTo(shape2.start) && shape1.end.equalTo(shape2.end)) {
        flag = Flatten.OVERLAP_SAME;
      } else if (shape1.start.equalTo(shape2.end) && shape1.end.equalTo(shape2.start)) {
        flag = Flatten.OVERLAP_OPPOSITE;
      }
    } else if (shape1 instanceof Flatten.Arc && shape2 instanceof Flatten.Arc) {
      if (shape1.start.equalTo(shape2.start) && shape1.end.equalTo(shape2.end) && shape1.middle().equalTo(shape2.middle())) {
        flag = Flatten.OVERLAP_SAME;
      } else if (shape1.start.equalTo(shape2.end) && shape1.end.equalTo(shape2.start) && shape1.middle().equalTo(shape2.middle())) {
        flag = Flatten.OVERLAP_OPPOSITE;
      }
    } else if (shape1 instanceof Flatten.Segment && shape2 instanceof Flatten.Arc || shape1 instanceof Flatten.Arc && shape2 instanceof Flatten.Segment) {
      if (shape1.start.equalTo(shape2.start) && shape1.end.equalTo(shape2.end) && shape1.middle().equalTo(shape2.middle())) {
        flag = Flatten.OVERLAP_SAME;
      } else if (shape1.start.equalTo(shape2.end) && shape1.end.equalTo(shape2.start) && shape1.middle().equalTo(shape2.middle())) {
        flag = Flatten.OVERLAP_OPPOSITE;
      }
    }
    if (this.overlap === undefined)
      this.overlap = flag;
    if (edge.overlap === undefined)
      edge.overlap = flag;
  }
  svg() {
    if (this.shape instanceof Flatten.Segment) {
      return ` L${this.shape.end.x},${this.shape.end.y}`;
    } else if (this.shape instanceof Flatten.Arc) {
      let arc = this.shape;
      let largeArcFlag;
      let sweepFlag = arc.counterClockwise ? "1" : "0";
      if (Flatten.Utils.EQ(arc.sweep, 2 * Math.PI)) {
        let sign = arc.counterClockwise ? 1 : -1;
        let halfArc1 = new Flatten.Arc(arc.pc, arc.r, arc.startAngle, arc.startAngle + sign * Math.PI, arc.counterClockwise);
        let halfArc2 = new Flatten.Arc(arc.pc, arc.r, arc.startAngle + sign * Math.PI, arc.endAngle, arc.counterClockwise);
        largeArcFlag = "0";
        return ` A${halfArc1.r},${halfArc1.r} 0 ${largeArcFlag},${sweepFlag} ${halfArc1.end.x},${halfArc1.end.y}
                    A${halfArc2.r},${halfArc2.r} 0 ${largeArcFlag},${sweepFlag} ${halfArc2.end.x},${halfArc2.end.y}`;
      } else {
        largeArcFlag = arc.sweep <= Math.PI ? "0" : "1";
        return ` A${arc.r},${arc.r} 0 ${largeArcFlag},${sweepFlag} ${arc.end.x},${arc.end.y}`;
      }
    }
  }
  toJSON() {
    return this.shape.toJSON();
  }
}
Flatten.Edge = Edge;

class CircularLinkedList extends LinkedList {
  constructor(first, last) {
    super(first, last);
    this.setCircularLinks();
  }
  setCircularLinks() {
    if (this.isEmpty())
      return;
    this.last.next = this.first;
    this.first.prev = this.last;
  }
  [Symbol.iterator]() {
    let element = undefined;
    return {
      next: () => {
        let value = element ? element : this.first;
        let done = this.first ? element ? element === this.first : false : true;
        element = value ? value.next : undefined;
        return { value, done };
      }
    };
  }
  append(element) {
    super.append(element);
    this.setCircularLinks();
    return this;
  }
  insert(newElement, elementBefore) {
    super.insert(newElement, elementBefore);
    this.setCircularLinks();
    return this;
  }
  remove(element) {
    super.remove(element);
    return this;
  }
}

class Face extends CircularLinkedList {
  constructor(polygon, ...args) {
    super();
    this._box = undefined;
    this._orientation = undefined;
    if (args.length === 0) {
      return;
    }
    if (args.length === 1) {
      if (args[0] instanceof Array) {
        let shapes = args[0];
        if (shapes.length === 0)
          return;
        if (shapes.every((shape) => {
          return shape instanceof Flatten.Point;
        })) {
          let segments = Face.points2segments(shapes);
          this.shapes2face(polygon.edges, segments);
        } else if (shapes.every((shape) => {
          return shape instanceof Array && shape.length === 2;
        })) {
          let points = shapes.map((shape) => new Flatten.Point(shape[0], shape[1]));
          let segments = Face.points2segments(points);
          this.shapes2face(polygon.edges, segments);
        } else if (shapes.every((shape) => {
          return shape instanceof Flatten.Segment || shape instanceof Flatten.Arc;
        })) {
          this.shapes2face(polygon.edges, shapes);
        } else if (shapes.every((shape) => {
          return shape.name === "segment" || shape.name === "arc";
        })) {
          let flattenShapes = [];
          for (let shape of shapes) {
            let flattenShape;
            if (shape.name === "segment") {
              flattenShape = new Flatten.Segment(shape);
            } else {
              flattenShape = new Flatten.Arc(shape);
            }
            flattenShapes.push(flattenShape);
          }
          this.shapes2face(polygon.edges, flattenShapes);
        }
      } else if (args[0] instanceof Face) {
        let face = args[0];
        this.first = face.first;
        this.last = face.last;
        for (let edge of face) {
          polygon.edges.add(edge);
        }
      } else if (args[0] instanceof Flatten.Circle) {
        this.shapes2face(polygon.edges, [args[0].toArc(CCW)]);
      } else if (args[0] instanceof Flatten.Box) {
        let box = args[0];
        this.shapes2face(polygon.edges, [
          new Flatten.Segment(new Flatten.Point(box.xmin, box.ymin), new Flatten.Point(box.xmax, box.ymin)),
          new Flatten.Segment(new Flatten.Point(box.xmax, box.ymin), new Flatten.Point(box.xmax, box.ymax)),
          new Flatten.Segment(new Flatten.Point(box.xmax, box.ymax), new Flatten.Point(box.xmin, box.ymax)),
          new Flatten.Segment(new Flatten.Point(box.xmin, box.ymax), new Flatten.Point(box.xmin, box.ymin))
        ]);
      }
    }
    if (args.length === 2 && args[0] instanceof Flatten.Edge && args[1] instanceof Flatten.Edge) {
      this.first = args[0];
      this.last = args[1];
      this.last.next = this.first;
      this.first.prev = this.last;
      this.setArcLength();
    }
  }
  get edges() {
    return this.toArray();
  }
  get vertices() {
    return this.edges.map((edge) => edge.shape.start.clone());
  }
  get shapes() {
    return this.edges.map((edge) => edge.shape.clone());
  }
  get box() {
    if (this._box === undefined) {
      let box = new Flatten.Box;
      for (let edge of this) {
        box = box.merge(edge.box);
      }
      this._box = box;
    }
    return this._box;
  }
  get perimeter() {
    return this.last.arc_length + this.last.length;
  }
  pointAtLength(length) {
    if (length > this.perimeter || length < 0)
      return null;
    let point = null;
    for (let edge of this) {
      if (length >= edge.arc_length && (edge === this.last || length < edge.next.arc_length)) {
        point = edge.pointAtLength(length - edge.arc_length);
        break;
      }
    }
    return point;
  }
  static points2segments(points) {
    let segments = [];
    for (let i = 0;i < points.length; i++) {
      if (points[i].equalTo(points[(i + 1) % points.length]))
        continue;
      segments.push(new Flatten.Segment(points[i], points[(i + 1) % points.length]));
    }
    return segments;
  }
  shapes2face(edges, shapes) {
    for (let shape of shapes) {
      let edge = new Flatten.Edge(shape);
      this.append(edge);
      edges.add(edge);
    }
  }
  append(edge) {
    super.append(edge);
    this.setOneEdgeArcLength(edge);
    edge.face = this;
    return this;
  }
  insert(newEdge, edgeBefore) {
    super.insert(newEdge, edgeBefore);
    this.setOneEdgeArcLength(newEdge);
    newEdge.face = this;
    return this;
  }
  remove(edge) {
    super.remove(edge);
    this.setArcLength();
    return this;
  }
  merge_with_next_edge(edge) {
    edge.shape.end.x = edge.next.shape.end.x;
    edge.shape.end.y = edge.next.shape.end.y;
    this.remove(edge.next);
    return this;
  }
  reverse() {
    let edges = [];
    let edge_tmp = this.last;
    do {
      edge_tmp.shape = edge_tmp.shape.reverse();
      edges.push(edge_tmp);
      edge_tmp = edge_tmp.prev;
    } while (edge_tmp !== this.last);
    this.first = undefined;
    this.last = undefined;
    for (let edge of edges) {
      if (this.first === undefined) {
        edge.prev = edge;
        edge.next = edge;
        this.first = edge;
        this.last = edge;
      } else {
        edge.prev = this.last;
        this.last.next = edge;
        this.last = edge;
        this.last.next = this.first;
        this.first.prev = this.last;
      }
      this.setOneEdgeArcLength(edge);
    }
    if (this._orientation !== undefined) {
      this._orientation = undefined;
      this._orientation = this.orientation();
    }
  }
  setArcLength() {
    for (let edge of this) {
      this.setOneEdgeArcLength(edge);
      edge.face = this;
    }
  }
  setOneEdgeArcLength(edge) {
    if (edge === this.first) {
      edge.arc_length = 0;
    } else {
      edge.arc_length = edge.prev.arc_length + edge.prev.length;
    }
  }
  area() {
    return Math.abs(this.signedArea());
  }
  signedArea() {
    let sArea = 0;
    let ymin = this.box.ymin;
    for (let edge of this) {
      sArea += edge.shape.definiteIntegral(ymin);
    }
    return sArea;
  }
  orientation() {
    if (this._orientation === undefined) {
      let area = this.signedArea();
      if (Flatten.Utils.EQ_0(area)) {
        this._orientation = ORIENTATION.NOT_ORIENTABLE;
      } else if (Flatten.Utils.LT(area, 0)) {
        this._orientation = ORIENTATION.CCW;
      } else {
        this._orientation = ORIENTATION.CW;
      }
    }
    return this._orientation;
  }
  isSimple(edges) {
    let ip = Face.getSelfIntersections(this, edges, true);
    return ip.length === 0;
  }
  static getSelfIntersections(face, edges, exitOnFirst = false) {
    let int_points = [];
    for (let edge1 of face) {
      let resp = edges.search(edge1.box);
      for (let edge2 of resp) {
        if (edge1 === edge2)
          continue;
        if (edge2.face !== face)
          continue;
        if (edge1.shape instanceof Flatten.Segment && edge2.shape instanceof Flatten.Segment && (edge1.next === edge2 || edge1.prev === edge2))
          continue;
        let ip = edge1.shape.intersect(edge2.shape);
        for (let pt of ip) {
          if (pt.equalTo(edge1.start) && pt.equalTo(edge2.end) && edge2 === edge1.prev)
            continue;
          if (pt.equalTo(edge1.end) && pt.equalTo(edge2.start) && edge2 === edge1.next)
            continue;
          int_points.push(pt);
          if (exitOnFirst)
            break;
        }
        if (int_points.length > 0 && exitOnFirst)
          break;
      }
      if (int_points.length > 0 && exitOnFirst)
        break;
    }
    return int_points;
  }
  findEdgeByPoint(pt) {
    let edgeFound;
    for (let edge of this) {
      if (pt.equalTo(edge.shape.start))
        continue;
      if (pt.equalTo(edge.shape.end) || edge.shape.contains(pt)) {
        edgeFound = edge;
        break;
      }
    }
    return edgeFound;
  }
  toPolygon() {
    return new Flatten.Polygon(this.shapes);
  }
  toJSON() {
    return this.edges.map((edge) => edge.toJSON());
  }
  svg() {
    let svgStr = `M${this.first.start.x},${this.first.start.y}`;
    for (let edge of this) {
      svgStr += edge.svg();
    }
    svgStr += ` z`;
    return svgStr;
  }
}
Flatten.Face = Face;

class Ray extends Shape {
  constructor(...args) {
    super();
    this.pt = new Flatten.Point;
    this.norm = new Flatten.Vector(0, 1);
    if (args.length === 0) {
      return;
    }
    if (args.length >= 1 && args[0] instanceof Flatten.Point) {
      this.pt = args[0].clone();
    }
    if (args.length === 1) {
      return;
    }
    if (args.length === 2 && args[1] instanceof Flatten.Vector) {
      this.norm = args[1].clone();
      return;
    }
    throw Errors.ILLEGAL_PARAMETERS;
  }
  clone() {
    return new Ray(this.pt, this.norm);
  }
  get slope() {
    let vec = new Flatten.Vector(this.norm.y, -this.norm.x);
    return vec.slope;
  }
  get box() {
    let slope = this.slope;
    return new Flatten.Box(slope > Math.PI / 2 && slope < 3 * Math.PI / 2 ? Number.NEGATIVE_INFINITY : this.pt.x, slope >= 0 && slope <= Math.PI ? this.pt.y : Number.NEGATIVE_INFINITY, slope >= Math.PI / 2 && slope <= 3 * Math.PI / 2 ? this.pt.x : Number.POSITIVE_INFINITY, slope >= Math.PI && slope <= 2 * Math.PI || slope === 0 ? this.pt.y : Number.POSITIVE_INFINITY);
  }
  get start() {
    return this.pt;
  }
  get end() {
    return;
  }
  get length() {
    return Number.POSITIVE_INFINITY;
  }
  contains(pt) {
    if (this.pt.equalTo(pt)) {
      return true;
    }
    let vec = new Flatten.Vector(this.pt, pt);
    return Flatten.Utils.EQ_0(this.norm.dot(vec)) && Flatten.Utils.GE(vec.cross(this.norm), 0);
  }
  coord(pt) {
    return vector$1(pt.x, pt.y).cross(this.norm);
  }
  split(pt) {
    if (!this.contains(pt))
      return [];
    if (this.pt.equalTo(pt)) {
      return [this];
    }
    return [
      new Flatten.Segment(this.pt, pt),
      new Flatten.Ray(pt, this.norm)
    ];
  }
  intersect(shape) {
    if (shape instanceof Flatten.Point) {
      return this.contains(shape) ? [shape] : [];
    }
    if (shape instanceof Flatten.Segment) {
      return intersectRay2Segment(this, shape);
    }
    if (shape instanceof Flatten.Arc) {
      return intersectRay2Arc(this, shape);
    }
    if (shape instanceof Flatten.Line) {
      return intersectRay2Line(this, shape);
    }
    if (shape instanceof Flatten.Ray) {
      return intersectRay2Ray(this, shape);
    }
    if (shape instanceof Flatten.Circle) {
      return intersectRay2Circle(this, shape);
    }
    if (shape instanceof Flatten.Box) {
      return intersectRay2Box(this, shape);
    }
    if (shape instanceof Flatten.Polygon) {
      return intersectRay2Polygon(this, shape);
    }
    if (shape instanceof Flatten.Multiline) {
      return intersectShape2Multiline(this, shape);
    }
  }
  rotate(angle, center = new Flatten.Point) {
    return new Flatten.Ray(this.pt.rotate(angle, center), this.norm.rotate(angle));
  }
  transform(m) {
    return new Flatten.Ray(this.pt.transform(m), this.norm.clone());
  }
  get name() {
    return "ray";
  }
  svg(box, attrs = {}) {
    let line = new Flatten.Line(this.pt, this.norm);
    let ip = intersectLine2Box(line, box);
    ip = ip.filter((pt) => this.contains(pt));
    if (ip.length === 0 || ip.length === 2)
      return "";
    let segment = new Flatten.Segment(this.pt, ip[0]);
    return segment.svg(attrs);
  }
}
Flatten.Ray = Ray;
var ray = (...args) => new Flatten.Ray(...args);
Flatten.ray = ray;
var Polygon$1 = class Polygon {
  constructor() {
    this.faces = new Flatten.PlanarSet;
    this.edges = new Flatten.PlanarSet;
    let args = [...arguments];
    if (args.length === 1 && (args[0] instanceof Array && args[0].length > 0 || args[0] instanceof Flatten.Circle || args[0] instanceof Flatten.Box)) {
      let argsArray = args[0];
      if (args[0] instanceof Array && args[0].every((loop) => {
        return loop instanceof Array;
      })) {
        if (argsArray.every((el) => {
          return el instanceof Array && el.length === 2 && typeof el[0] === "number" && typeof el[1] === "number";
        })) {
          this.faces.add(new Flatten.Face(this, argsArray));
        } else {
          for (let loop of argsArray) {
            if (loop instanceof Array && loop[0] instanceof Array && loop[0].every((el) => {
              return el instanceof Array && el.length === 2 && typeof el[0] === "number" && typeof el[1] === "number";
            })) {
              for (let loop1 of loop) {
                this.faces.add(new Flatten.Face(this, loop1));
              }
            } else {
              this.faces.add(new Flatten.Face(this, loop));
            }
          }
        }
      } else {
        this.faces.add(new Flatten.Face(this, argsArray));
      }
    }
  }
  get box() {
    return [...this.faces].reduce((acc, face) => acc.merge(face.box), new Flatten.Box);
  }
  get vertices() {
    return [...this.faces].flatMap((face) => face.vertices);
  }
  clone() {
    let polygon = new Polygon;
    for (let face of this.faces) {
      polygon.addFace(face.shapes);
    }
    return polygon;
  }
  createFromArray(polygons) {
    const newPolygon = new Polygon;
    polygons.forEach((polygon) => [...polygon.faces].forEach((face) => newPolygon.addFace(face.shapes)));
    return newPolygon;
  }
  isEmpty() {
    return this.edges.size === 0 || this.faces.size === 0;
  }
  isValid() {
    let valid = true;
    for (let face of this.faces) {
      if (!face.isSimple(this.edges)) {
        valid = false;
        break;
      }
    }
    return valid;
  }
  area() {
    let signedArea = [...this.faces].reduce((acc, face) => acc + face.signedArea(), 0);
    return Math.abs(signedArea);
  }
  addFace(...args) {
    let face = new Flatten.Face(this, ...args);
    this.faces.add(face);
    return face;
  }
  deleteFace(face) {
    for (let edge of face) {
      this.edges.delete(edge);
    }
    return this.faces.delete(face);
  }
  recreateFaces() {
    this.faces.clear();
    for (let edge of this.edges) {
      edge.face = null;
    }
    let first;
    let unassignedEdgeFound = true;
    while (unassignedEdgeFound) {
      unassignedEdgeFound = false;
      for (let edge of this.edges) {
        if (edge.face === null) {
          first = edge;
          unassignedEdgeFound = true;
          break;
        }
      }
      if (unassignedEdgeFound) {
        let last = first;
        do {
          last = last.next;
        } while (last.next !== first);
        this.addFace(first, last);
      }
    }
  }
  removeChain(face, edgeFrom, edgeTo) {
    if (edgeTo.next === edgeFrom) {
      this.deleteFace(face);
      return;
    }
    for (let edge = edgeFrom;edge !== edgeTo.next; edge = edge.next) {
      face.remove(edge);
      this.edges.delete(edge);
      if (face.isEmpty()) {
        this.deleteFace(face);
        break;
      }
    }
  }
  addVertex(pt, edge) {
    let shapes = edge.shape.split(pt);
    if (shapes[0] === null)
      return edge.prev;
    if (shapes[1] === null)
      return edge;
    let newEdge = new Flatten.Edge(shapes[0]);
    let edgeBefore = edge.prev;
    edge.face.insert(newEdge, edgeBefore);
    this.edges.delete(edge);
    this.edges.add(newEdge);
    edge.shape = shapes[1];
    this.edges.add(edge);
    return newEdge;
  }
  removeEndVertex(edge) {
    const edge_next = edge.next;
    if (edge_next === edge)
      return;
    edge.face.merge_with_next_edge(edge);
    this.edges.delete(edge_next);
  }
  cut(multiline) {
    const polygons = this.splitToIslands();
    const result = polygons.flatMap((polygon) => polygon._cutSingleIsland(multiline)).filter((polygon) => polygon.isValid() && polygon.isEmpty() === false);
    return this.createFromArray(result);
  }
  _cutSingleIsland(inputMultiline) {
    let newPoly = this.clone();
    const multiline = inputMultiline.clone();
    let intersections = {
      int_points1: [],
      int_points2: [],
      int_points1_sorted: [],
      int_points2_sorted: []
    };
    for (let edge1 of multiline.edges) {
      for (let edge2 of newPoly.edges) {
        let ip = intersectEdge2Edge(edge1, edge2);
        for (let pt of ip) {
          addToIntPoints(edge1, pt, intersections.int_points1);
          addToIntPoints(edge2, pt, intersections.int_points2);
        }
      }
    }
    if (intersections.int_points1.length === 0)
      return newPoly;
    intersections.int_points1_sorted = getSortedArray(intersections.int_points1);
    intersections.int_points2_sorted = getSortedArray(intersections.int_points2);
    splitByIntersections(multiline, intersections.int_points1_sorted);
    splitByIntersections(newPoly, intersections.int_points2_sorted);
    filterDuplicatedIntersections(intersections);
    intersections.int_points1_sorted = getSortedArray(intersections.int_points1);
    intersections.int_points2_sorted = getSortedArray(intersections.int_points2);
    initializeInclusionFlags(intersections.int_points1);
    calculateInclusionFlags(intersections.int_points1, newPoly);
    for (let int_point1 of intersections.int_points1_sorted) {
      if (int_point1.edge_before && int_point1.edge_after && int_point1.edge_before.bv === int_point1.edge_after.bv) {
        intersections.int_points2[int_point1.id] = -1;
        int_point1.id = -1;
      }
    }
    intersections.int_points1 = intersections.int_points1.filter((int_point) => int_point.id >= 0);
    intersections.int_points2 = intersections.int_points2.filter((int_point) => int_point.id >= 0);
    intersections.int_points1.forEach((int_point, index) => {
      int_point.id = index;
    });
    intersections.int_points2.forEach((int_point, index) => {
      int_point.id = index;
    });
    if (intersections.int_points1.length === 0)
      return newPoly;
    intersections.int_points1_sorted = getSortedArray(intersections.int_points1);
    intersections.int_points2_sorted = getSortedArray(intersections.int_points2);
    let int_point1_prev;
    let int_point1_curr;
    for (let i = 1;i < intersections.int_points1_sorted.length; i++) {
      int_point1_curr = intersections.int_points1_sorted[i];
      int_point1_prev = intersections.int_points1_sorted[i - 1];
      if (int_point1_curr.edge_before && int_point1_curr.edge_before.bv === INSIDE$2) {
        let edgeFrom = int_point1_prev.edge_after;
        let edgeTo = int_point1_curr.edge_before;
        let newEdges = multiline.getChain(edgeFrom, edgeTo);
        insertBetweenIntPoints(intersections.int_points2[int_point1_prev.id], intersections.int_points2[int_point1_curr.id], newEdges);
        newEdges.forEach((edge) => newPoly.edges.add(edge));
        newEdges = newEdges.reverse().map((edge) => new Flatten.Edge(edge.shape.reverse()));
        for (let k = 0;k < newEdges.length - 1; k++) {
          newEdges[k].next = newEdges[k + 1];
          newEdges[k + 1].prev = newEdges[k];
        }
        insertBetweenIntPoints(intersections.int_points2[int_point1_curr.id], intersections.int_points2[int_point1_prev.id], newEdges);
        newEdges.forEach((edge) => newPoly.edges.add(edge));
      }
    }
    newPoly.recreateFaces();
    return newPoly;
  }
  cutWithLine(line) {
    let multiline = new Multiline$1([line]);
    return this.cut(multiline);
  }
  findEdgeByPoint(pt) {
    let edge;
    for (let face of this.faces) {
      edge = face.findEdgeByPoint(pt);
      if (edge !== undefined)
        break;
    }
    return edge;
  }
  splitToIslands() {
    if (this.isEmpty())
      return [];
    let polygons = this.toArray();
    polygons.sort((polygon1, polygon2) => polygon2.area() - polygon1.area());
    let orientation = [...polygons[0].faces][0].orientation();
    let newPolygons = polygons.filter((polygon) => [...polygon.faces][0].orientation() === orientation);
    for (let polygon of polygons) {
      let face = [...polygon.faces][0];
      if (face.orientation() === orientation)
        continue;
      for (let islandPolygon of newPolygons) {
        if (face.shapes.every((shape) => islandPolygon.contains(shape))) {
          islandPolygon.addFace(face.shapes);
          break;
        }
      }
    }
    return newPolygons;
  }
  rearrange() {
    if (this.faces.size <= 1)
      return this.clone();
    const islands = this.splitToIslands();
    const newPolygon = new Polygon;
    islands.forEach((island) => {
      island.faces.forEach((face) => newPolygon.addFace(face.shapes));
    });
    return newPolygon;
  }
  orientation() {
    if (this.isEmpty())
      return ORIENTATION.NOT_ORIENTABLE;
    return [...this.faces][0].orientation();
  }
  isOuter(face) {
    return face.orientation() === this.orientation();
  }
  isMultiPolygon() {
    let outerCounter = 0;
    this.faces.forEach((face) => {
      if (this.isOuter(face))
        outerCounter++;
    });
    return outerCounter > 1;
  }
  reverse() {
    for (let face of this.faces) {
      face.reverse();
    }
    return this;
  }
  contains(shape) {
    if (shape instanceof Flatten.Point) {
      let rel = ray_shoot(this, shape);
      return rel === INSIDE$2 || rel === BOUNDARY$1;
    } else {
      return cover(this, shape);
    }
  }
  distanceTo(shape) {
    if (shape instanceof Flatten.Point) {
      let [dist, shortest_segment] = Flatten.Distance.point2polygon(shape, this);
      shortest_segment = shortest_segment.reverse();
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Circle || shape instanceof Flatten.Line || shape instanceof Flatten.Segment || shape instanceof Flatten.Arc) {
      let [dist, shortest_segment] = Flatten.Distance.shape2polygon(shape, this);
      shortest_segment = shortest_segment.reverse();
      return [dist, shortest_segment];
    }
    if (shape instanceof Flatten.Box) {
      return this.distanceTo(new Flatten.Polygon(shape));
    }
    if (shape instanceof Flatten.Polygon) {
      let min_dist_and_segment = [Number.POSITIVE_INFINITY, new Flatten.Segment];
      let dist, shortest_segment;
      for (let edge of this.edges) {
        let min_stop = min_dist_and_segment[0];
        [dist, shortest_segment] = Flatten.Distance.shape2planarSet(edge.shape, shape.edges, min_stop);
        if (Flatten.Utils.LT(dist, min_stop)) {
          min_dist_and_segment = [dist, shortest_segment];
        }
      }
      return min_dist_and_segment;
    }
  }
  intersect(shape) {
    if (shape instanceof Flatten.Point) {
      return this.contains(shape) ? [shape] : [];
    }
    if (shape instanceof Flatten.Line) {
      return intersectLine2Polygon(shape, this);
    }
    if (shape instanceof Flatten.Ray) {
      return intersectRay2Polygon(shape, this);
    }
    if (shape instanceof Flatten.Circle) {
      return intersectCircle2Polygon(shape, this);
    }
    if (shape instanceof Flatten.Segment) {
      return intersectSegment2Polygon(shape, this);
    }
    if (shape instanceof Flatten.Arc) {
      return intersectArc2Polygon(shape, this);
    }
    if (shape instanceof Flatten.Polygon) {
      return intersectPolygon2Polygon(shape, this);
    }
    if (shape instanceof Flatten.Multiline) {
      return intersectMultiline2Polygon(shape, this);
    }
  }
  translate(vec) {
    let newPolygon = new Polygon;
    for (let face of this.faces) {
      newPolygon.addFace(face.shapes.map((shape) => shape.translate(vec)));
    }
    return newPolygon;
  }
  rotate(angle = 0, center = new Flatten.Point) {
    let newPolygon = new Polygon;
    for (let face of this.faces) {
      newPolygon.addFace(face.shapes.map((shape) => shape.rotate(angle, center)));
    }
    return newPolygon;
  }
  scale(sx, sy) {
    let newPolygon = new Polygon;
    for (let face of this.faces) {
      newPolygon.addFace(face.shapes.map((shape) => shape.scale(sx, sy)));
    }
    return newPolygon;
  }
  transform(matrix = new Flatten.Matrix) {
    let newPolygon = new Polygon;
    for (let face of this.faces) {
      newPolygon.addFace(face.shapes.map((shape) => shape.transform(matrix)));
    }
    return newPolygon;
  }
  toJSON() {
    return [...this.faces].map((face) => face.toJSON());
  }
  toArray() {
    return [...this.faces].map((face) => face.toPolygon());
  }
  dpath() {
    return [...this.faces].reduce((acc, face) => acc + face.svg(), "");
  }
  svg(attrs = {}) {
    let svgStr = `
<path ${convertToString({ fillRule: "evenodd", fill: "lightcyan", ...attrs })} d="`;
    for (let face of this.faces) {
      svgStr += `
${face.svg()}`;
    }
    svgStr += `" >
</path>`;
    return svgStr;
  }
};
Flatten.Polygon = Polygon$1;
var polygon = (...args) => new Flatten.Polygon(...args);
Flatten.polygon = polygon;
var { Circle, Line, Point: Point$1, Vector, Utils } = Flatten;

class Inversion {
  constructor(inversion_circle) {
    this.circle = inversion_circle;
  }
  get inversion_circle() {
    return this.circle;
  }
  static inversePoint(inversion_circle, point) {
    const v = new Vector(inversion_circle.pc, point);
    const k2 = inversion_circle.r * inversion_circle.r;
    const len2 = v.dot(v);
    const reflected_point = Utils.EQ_0(len2) ? new Point$1(Number.POSITIVE_INFINITY, Number.POSITIVE_INFINITY) : inversion_circle.pc.translate(v.multiply(k2 / len2));
    return reflected_point;
  }
  static inverseCircle(inversion_circle, circle) {
    const dist = inversion_circle.pc.distanceTo(circle.pc)[0];
    if (Utils.EQ(dist, circle.r)) {
      let d = inversion_circle.r * inversion_circle.r / (2 * circle.r);
      let v = new Vector(inversion_circle.pc, circle.pc);
      v = v.normalize();
      let pt = inversion_circle.pc.translate(v.multiply(d));
      return new Line(pt, v);
    } else {
      let v = new Vector(inversion_circle.pc, circle.pc);
      let s = inversion_circle.r * inversion_circle.r / (v.dot(v) - circle.r * circle.r);
      let pc = inversion_circle.pc.translate(v.multiply(s));
      let r = Math.abs(s) * circle.r;
      return new Circle(pc, r);
    }
  }
  static inverseLine(inversion_circle, line) {
    const [dist, shortest_segment] = inversion_circle.pc.distanceTo(line);
    if (Utils.EQ_0(dist)) {
      return line.clone();
    } else {
      let r = inversion_circle.r * inversion_circle.r / (2 * dist);
      let v = new Vector(inversion_circle.pc, shortest_segment.end);
      v = v.multiply(r / dist);
      return new Circle(inversion_circle.pc.translate(v), r);
    }
  }
  inverse(shape) {
    if (shape instanceof Point$1) {
      return Inversion.inversePoint(this.circle, shape);
    } else if (shape instanceof Circle) {
      return Inversion.inverseCircle(this.circle, shape);
    } else if (shape instanceof Line) {
      return Inversion.inverseLine(this.circle, shape);
    }
  }
}
Flatten.Inversion = Inversion;
var inversion = (circle) => new Flatten.Inversion(circle);
Flatten.inversion = inversion;

class Distance {
  static point2point(pt1, pt2) {
    return pt1.distanceTo(pt2);
  }
  static point2line(pt, line) {
    let closest_point = pt.projectionOn(line);
    let vec = new Flatten.Vector(pt, closest_point);
    return [vec.length, new Flatten.Segment(pt, closest_point)];
  }
  static point2circle(pt, circle) {
    let [dist2center, shortest_dist] = pt.distanceTo(circle.center);
    if (Flatten.Utils.EQ_0(dist2center)) {
      return [circle.r, new Flatten.Segment(pt, circle.toArc().start)];
    } else {
      let dist = Math.abs(dist2center - circle.r);
      let v = new Flatten.Vector(circle.pc, pt).normalize().multiply(circle.r);
      let closest_point = circle.pc.translate(v);
      return [dist, new Flatten.Segment(pt, closest_point)];
    }
  }
  static point2segment(pt, segment) {
    if (segment.start.equalTo(segment.end)) {
      return Distance.point2point(pt, segment.start);
    }
    let v_seg = new Flatten.Vector(segment.start, segment.end);
    let v_ps2pt = new Flatten.Vector(segment.start, pt);
    let v_pe2pt = new Flatten.Vector(segment.end, pt);
    let start_sp = v_seg.dot(v_ps2pt);
    let end_sp = -v_seg.dot(v_pe2pt);
    let dist;
    let closest_point;
    if (Flatten.Utils.GE(start_sp, 0) && Flatten.Utils.GE(end_sp, 0)) {
      let v_unit = segment.tangentInStart();
      dist = Math.abs(v_unit.cross(v_ps2pt));
      closest_point = segment.start.translate(v_unit.multiply(v_unit.dot(v_ps2pt)));
      return [dist, new Flatten.Segment(pt, closest_point)];
    } else if (start_sp < 0) {
      return pt.distanceTo(segment.start);
    } else {
      return pt.distanceTo(segment.end);
    }
  }
  static point2arc(pt, arc) {
    let circle = new Flatten.Circle(arc.pc, arc.r);
    let dist_and_segment = [];
    let dist, shortest_segment;
    [dist, shortest_segment] = Distance.point2circle(pt, circle);
    if (shortest_segment.end.on(arc)) {
      dist_and_segment.push(Distance.point2circle(pt, circle));
    }
    dist_and_segment.push(Distance.point2point(pt, arc.start));
    dist_and_segment.push(Distance.point2point(pt, arc.end));
    Distance.sort(dist_and_segment);
    return dist_and_segment[0];
  }
  static point2edge(pt, edge) {
    return edge.shape instanceof Flatten.Segment ? Distance.point2segment(pt, edge.shape) : Distance.point2arc(pt, edge.shape);
  }
  static segment2line(seg, line) {
    let ip = seg.intersect(line);
    if (ip.length > 0) {
      return [0, new Flatten.Segment(ip[0], ip[0])];
    }
    let dist_and_segment = [];
    dist_and_segment.push(Distance.point2line(seg.start, line));
    dist_and_segment.push(Distance.point2line(seg.end, line));
    Distance.sort(dist_and_segment);
    return dist_and_segment[0];
  }
  static segment2segment(seg1, seg2) {
    let ip = intersectSegment2Segment(seg1, seg2);
    if (ip.length > 0) {
      return [0, new Flatten.Segment(ip[0], ip[0])];
    }
    let dist_and_segment = [];
    let dist_tmp, shortest_segment_tmp;
    [dist_tmp, shortest_segment_tmp] = Distance.point2segment(seg2.start, seg1);
    dist_and_segment.push([dist_tmp, shortest_segment_tmp.reverse()]);
    [dist_tmp, shortest_segment_tmp] = Distance.point2segment(seg2.end, seg1);
    dist_and_segment.push([dist_tmp, shortest_segment_tmp.reverse()]);
    dist_and_segment.push(Distance.point2segment(seg1.start, seg2));
    dist_and_segment.push(Distance.point2segment(seg1.end, seg2));
    Distance.sort(dist_and_segment);
    return dist_and_segment[0];
  }
  static segment2circle(seg, circle) {
    let ip = seg.intersect(circle);
    if (ip.length > 0) {
      return [0, new Flatten.Segment(ip[0], ip[0])];
    }
    let line = new Flatten.Line(seg.ps, seg.pe);
    let [dist, shortest_segment] = Distance.point2line(circle.center, line);
    if (Flatten.Utils.GE(dist, circle.r) && shortest_segment.end.on(seg)) {
      return Distance.point2circle(shortest_segment.end, circle);
    } else {
      let [dist_from_start, shortest_segment_from_start] = Distance.point2circle(seg.start, circle);
      let [dist_from_end, shortest_segment_from_end] = Distance.point2circle(seg.end, circle);
      return Flatten.Utils.LT(dist_from_start, dist_from_end) ? [dist_from_start, shortest_segment_from_start] : [dist_from_end, shortest_segment_from_end];
    }
  }
  static segment2arc(seg, arc) {
    let ip = seg.intersect(arc);
    if (ip.length > 0) {
      return [0, new Flatten.Segment(ip[0], ip[0])];
    }
    let line = new Flatten.Line(seg.ps, seg.pe);
    let circle = new Flatten.Circle(arc.pc, arc.r);
    let [dist_from_center, shortest_segment_from_center] = Distance.point2line(circle.center, line);
    if (Flatten.Utils.GE(dist_from_center, circle.r) && shortest_segment_from_center.end.on(seg)) {
      let [dist_from_projection, shortest_segment_from_projection] = Distance.point2circle(shortest_segment_from_center.end, circle);
      if (shortest_segment_from_projection.end.on(arc)) {
        return [dist_from_projection, shortest_segment_from_projection];
      }
    }
    let dist_and_segment = [];
    dist_and_segment.push(Distance.point2arc(seg.start, arc));
    dist_and_segment.push(Distance.point2arc(seg.end, arc));
    let dist_tmp, segment_tmp;
    [dist_tmp, segment_tmp] = Distance.point2segment(arc.start, seg);
    dist_and_segment.push([dist_tmp, segment_tmp.reverse()]);
    [dist_tmp, segment_tmp] = Distance.point2segment(arc.end, seg);
    dist_and_segment.push([dist_tmp, segment_tmp.reverse()]);
    Distance.sort(dist_and_segment);
    return dist_and_segment[0];
  }
  static circle2circle(circle1, circle2) {
    let ip = circle1.intersect(circle2);
    if (ip.length > 0) {
      return [0, new Flatten.Segment(ip[0], ip[0])];
    }
    if (circle1.center.equalTo(circle2.center)) {
      let arc1 = circle1.toArc();
      let arc2 = circle2.toArc();
      return Distance.point2point(arc1.start, arc2.start);
    } else {
      let line = new Flatten.Line(circle1.center, circle2.center);
      let ip1 = line.intersect(circle1);
      let ip2 = line.intersect(circle2);
      let dist_and_segment = [];
      dist_and_segment.push(Distance.point2point(ip1[0], ip2[0]));
      dist_and_segment.push(Distance.point2point(ip1[0], ip2[1]));
      dist_and_segment.push(Distance.point2point(ip1[1], ip2[0]));
      dist_and_segment.push(Distance.point2point(ip1[1], ip2[1]));
      Distance.sort(dist_and_segment);
      return dist_and_segment[0];
    }
  }
  static circle2line(circle, line) {
    let ip = circle.intersect(line);
    if (ip.length > 0) {
      return [0, new Flatten.Segment(ip[0], ip[0])];
    }
    let [dist_from_center, shortest_segment_from_center] = Distance.point2line(circle.center, line);
    let [dist, shortest_segment] = Distance.point2circle(shortest_segment_from_center.end, circle);
    shortest_segment = shortest_segment.reverse();
    return [dist, shortest_segment];
  }
  static arc2line(arc, line) {
    let ip = line.intersect(arc);
    if (ip.length > 0) {
      return [0, new Flatten.Segment(ip[0], ip[0])];
    }
    let circle = new Flatten.Circle(arc.center, arc.r);
    let [dist_from_center, shortest_segment_from_center] = Distance.point2line(circle.center, line);
    if (Flatten.Utils.GE(dist_from_center, circle.r)) {
      let [dist_from_projection, shortest_segment_from_projection] = Distance.point2circle(shortest_segment_from_center.end, circle);
      if (shortest_segment_from_projection.end.on(arc)) {
        return [dist_from_projection, shortest_segment_from_projection];
      }
    } else {
      let dist_and_segment = [];
      dist_and_segment.push(Distance.point2line(arc.start, line));
      dist_and_segment.push(Distance.point2line(arc.end, line));
      Distance.sort(dist_and_segment);
      return dist_and_segment[0];
    }
  }
  static arc2circle(arc, circle2) {
    let ip = arc.intersect(circle2);
    if (ip.length > 0) {
      return [0, new Flatten.Segment(ip[0], ip[0])];
    }
    let circle1 = new Flatten.Circle(arc.center, arc.r);
    let [dist, shortest_segment] = Distance.circle2circle(circle1, circle2);
    if (shortest_segment.start.on(arc)) {
      return [dist, shortest_segment];
    } else {
      let dist_and_segment = [];
      dist_and_segment.push(Distance.point2circle(arc.start, circle2));
      dist_and_segment.push(Distance.point2circle(arc.end, circle2));
      Distance.sort(dist_and_segment);
      return dist_and_segment[0];
    }
  }
  static arc2arc(arc1, arc2) {
    let ip = arc1.intersect(arc2);
    if (ip.length > 0) {
      return [0, new Flatten.Segment(ip[0], ip[0])];
    }
    let circle1 = new Flatten.Circle(arc1.center, arc1.r);
    let circle2 = new Flatten.Circle(arc2.center, arc2.r);
    let [dist, shortest_segment] = Distance.circle2circle(circle1, circle2);
    if (shortest_segment.start.on(arc1) && shortest_segment.end.on(arc2)) {
      return [dist, shortest_segment];
    } else {
      let dist_and_segment = [];
      let dist_tmp, segment_tmp;
      [dist_tmp, segment_tmp] = Distance.point2arc(arc1.start, arc2);
      if (segment_tmp.end.on(arc2)) {
        dist_and_segment.push([dist_tmp, segment_tmp]);
      }
      [dist_tmp, segment_tmp] = Distance.point2arc(arc1.end, arc2);
      if (segment_tmp.end.on(arc2)) {
        dist_and_segment.push([dist_tmp, segment_tmp]);
      }
      [dist_tmp, segment_tmp] = Distance.point2arc(arc2.start, arc1);
      if (segment_tmp.end.on(arc1)) {
        dist_and_segment.push([dist_tmp, segment_tmp.reverse()]);
      }
      [dist_tmp, segment_tmp] = Distance.point2arc(arc2.end, arc1);
      if (segment_tmp.end.on(arc1)) {
        dist_and_segment.push([dist_tmp, segment_tmp.reverse()]);
      }
      [dist_tmp, segment_tmp] = Distance.point2point(arc1.start, arc2.start);
      dist_and_segment.push([dist_tmp, segment_tmp]);
      [dist_tmp, segment_tmp] = Distance.point2point(arc1.start, arc2.end);
      dist_and_segment.push([dist_tmp, segment_tmp]);
      [dist_tmp, segment_tmp] = Distance.point2point(arc1.end, arc2.start);
      dist_and_segment.push([dist_tmp, segment_tmp]);
      [dist_tmp, segment_tmp] = Distance.point2point(arc1.end, arc2.end);
      dist_and_segment.push([dist_tmp, segment_tmp]);
      Distance.sort(dist_and_segment);
      return dist_and_segment[0];
    }
  }
  static point2polygon(point, polygon) {
    let min_dist_and_segment = [Number.POSITIVE_INFINITY, new Flatten.Segment];
    for (let edge of polygon.edges) {
      let [dist, shortest_segment] = Distance.point2edge(point, edge);
      if (Flatten.Utils.LT(dist, min_dist_and_segment[0])) {
        min_dist_and_segment = [dist, shortest_segment];
      }
    }
    return min_dist_and_segment;
  }
  static shape2polygon(shape, polygon) {
    let min_dist_and_segment = [Number.POSITIVE_INFINITY, new Flatten.Segment];
    for (let edge of polygon.edges) {
      let [dist, shortest_segment] = shape.distanceTo(edge.shape);
      if (Flatten.Utils.LT(dist, min_dist_and_segment[0])) {
        min_dist_and_segment = [dist, shortest_segment];
      }
    }
    return min_dist_and_segment;
  }
  static polygon2polygon(polygon1, polygon2) {
    let min_dist_and_segment = [Number.POSITIVE_INFINITY, new Flatten.Segment];
    for (let edge1 of polygon1.edges) {
      for (let edge2 of polygon2.edges) {
        let [dist, shortest_segment] = edge1.shape.distanceTo(edge2.shape);
        if (Flatten.Utils.LT(dist, min_dist_and_segment[0])) {
          min_dist_and_segment = [dist, shortest_segment];
        }
      }
    }
    return min_dist_and_segment;
  }
  static box2box_minmax(box1, box2) {
    let mindist_x = Math.max(Math.max(box1.xmin - box2.xmax, 0), Math.max(box2.xmin - box1.xmax, 0));
    let mindist_y = Math.max(Math.max(box1.ymin - box2.ymax, 0), Math.max(box2.ymin - box1.ymax, 0));
    let mindist = mindist_x * mindist_x + mindist_y * mindist_y;
    let box = box1.merge(box2);
    let dx = box.xmax - box.xmin;
    let dy = box.ymax - box.ymin;
    let maxdist = dx * dx + dy * dy;
    return [mindist, maxdist];
  }
  static minmax_tree_process_level(shape, level, min_stop, tree) {
    let mindist, maxdist;
    for (let node of level) {
      [mindist, maxdist] = Distance.box2box_minmax(shape.box, node.item.key);
      for (let value of node.item.values) {
        if (value instanceof Flatten.Edge) {
          tree.insert([mindist, maxdist], value.shape);
        } else {
          tree.insert([mindist, maxdist], value);
        }
      }
      if (Flatten.Utils.LT(maxdist, min_stop)) {
        min_stop = maxdist;
      }
    }
    if (level.length === 0)
      return min_stop;
    let new_level_left = level.map((node) => node.left.isNil() ? undefined : node.left).filter((node) => node !== undefined);
    let new_level_right = level.map((node) => node.right.isNil() ? undefined : node.right).filter((node) => node !== undefined);
    let new_level = [...new_level_left, ...new_level_right].filter((node) => {
      let [mindist, maxdist] = Distance.box2box_minmax(shape.box, node.max);
      return Flatten.Utils.LE(mindist, min_stop);
    });
    min_stop = Distance.minmax_tree_process_level(shape, new_level, min_stop, tree);
    return min_stop;
  }
  static minmax_tree(shape, set, min_stop) {
    let tree = new IntervalTree;
    let level = [set.index.root];
    let squared_min_stop = min_stop < Number.POSITIVE_INFINITY ? min_stop * min_stop : Number.POSITIVE_INFINITY;
    squared_min_stop = Distance.minmax_tree_process_level(shape, level, squared_min_stop, tree);
    return tree;
  }
  static minmax_tree_calc_distance(shape, node, min_dist_and_segment) {
    let min_dist_and_segment_new, stop;
    if (node != null && !node.isNil()) {
      [min_dist_and_segment_new, stop] = Distance.minmax_tree_calc_distance(shape, node.left, min_dist_and_segment);
      if (stop) {
        return [min_dist_and_segment_new, stop];
      }
      if (Flatten.Utils.LT(min_dist_and_segment_new[0], Math.sqrt(node.item.key.low))) {
        return [min_dist_and_segment_new, true];
      }
      let [dist, shortest_segment] = Distance.distanceToArray(shape, node.item.values);
      if (Flatten.Utils.LT(dist, min_dist_and_segment_new[0])) {
        min_dist_and_segment_new = [dist, shortest_segment];
      }
      [min_dist_and_segment_new, stop] = Distance.minmax_tree_calc_distance(shape, node.right, min_dist_and_segment_new);
      return [min_dist_and_segment_new, stop];
    }
    return [min_dist_and_segment, false];
  }
  static shape2planarSet(shape, set, min_stop = Number.POSITIVE_INFINITY) {
    let min_dist_and_segment = [min_stop, new Flatten.Segment];
    let stop = false;
    if (set instanceof Flatten.PlanarSet) {
      let tree = Distance.minmax_tree(shape, set, min_stop);
      [min_dist_and_segment, stop] = Distance.minmax_tree_calc_distance(shape, tree.root, min_dist_and_segment);
    }
    return min_dist_and_segment;
  }
  static sort(dist_and_segment) {
    dist_and_segment.sort((d1, d2) => {
      if (Flatten.Utils.LT(d1[0], d2[0])) {
        return -1;
      }
      if (Flatten.Utils.GT(d1[0], d2[0])) {
        return 1;
      }
      return 0;
    });
  }
  static distance(shape1, shape2) {
    return shape1.distanceTo(shape2);
  }
  static distanceToArray(shape1, shapes) {
    let min_dist_and_segment = [Number.POSITIVE_INFINITY, new Flatten.Segment];
    for (let shape2 of shapes) {
      let [dist, shortest_segment] = shape1.distanceTo(shape2);
      if (Flatten.Utils.LT(dist, min_dist_and_segment[0])) {
        min_dist_and_segment = [dist, shortest_segment];
      }
    }
    return min_dist_and_segment;
  }
  static shape2multiline(shape, multiline) {
    let min_dist_and_segment = [Number.POSITIVE_INFINITY, new Flatten.Segment];
    for (let edge of multiline) {
      let [dist, shortest_segment] = Distance.distance(shape, edge.shape);
      if (Flatten.Utils.LT(dist, min_dist_and_segment[0])) {
        min_dist_and_segment = [dist, shortest_segment];
      }
    }
    return min_dist_and_segment;
  }
  static multiline2multiline(multiline1, multiline2) {
    let min_dist_and_segment = [Number.POSITIVE_INFINITY, new Flatten.Segment];
    for (let edge1 of multiline1) {
      for (let edge2 of multiline2) {
        let [dist, shortest_segment] = Distance.distance(edge1.shape, edge2.shape);
        if (Flatten.Utils.LT(dist, min_dist_and_segment[0])) {
          min_dist_and_segment = [dist, shortest_segment];
        }
      }
    }
    return min_dist_and_segment;
  }
}
Flatten.Distance = Distance;
var { Multiline, Point, Segment, Polygon } = Flatten;
function parseSinglePoint(pointStr) {
  return new Point(pointStr.split(" ").map(Number));
}
function parseMultiPoint(multipointStr) {
  return multipointStr.split(", ").map(parseSinglePoint);
}
function parseLineString(lineStr) {
  const points = parseMultiPoint(lineStr);
  let segments = [];
  for (let i = 0;i < points.length - 1; i++) {
    segments.push(new Segment(points[i], points[i + 1]));
  }
  return new Multiline(segments);
}
function parseMultiLineString(multilineStr) {
  const lineStrings = multilineStr.replace(/\(\(/, "").replace(/\)\)$/, "").split("), (");
  return lineStrings.map(parseLineString);
}
function parseSinglePolygon(polygonStr) {
  const facesStr = polygonStr.replace(/\(\(/, "").replace(/\)\)$/, "").split("), (");
  const polygon = new Polygon;
  let orientation;
  facesStr.forEach((facesStr, idx) => {
    let points = facesStr.split(", ").map((coordStr) => {
      return new Point(coordStr.split(" ").map(Number));
    });
    const face = polygon.addFace(points);
    if (idx === 0) {
      orientation = face.orientation();
    } else {
      if (face.orientation() === orientation) {
        face.reverse();
      }
    }
  });
  return polygon;
}
function parseMutliPolygon(multiPolygonString) {
  const polygonStrings = multiPolygonString.split(/\)\), \(\(/).map((polygon) => "((" + polygon + "))");
  const polygons = polygonStrings.map(parseSinglePolygon);
  const polygon = new Polygon;
  const faces = polygons.reduce((acc, polygon) => [...acc, ...polygon?.faces], []);
  faces.forEach((face) => polygon.addFace([...face?.shapes]));
  return polygon;
}
function parsePolygon(wkt) {
  if (wkt.startsWith("POLYGON")) {
    const polygonStr = wkt.replace(/^POLYGON /, "");
    return parseSinglePolygon(polygonStr);
  } else {
    const multiPolygonString = wkt.replace(/^MULTIPOLYGON \(\(\((.*)\)\)\)$/, "$1");
    return parseMutliPolygon(multiPolygonString);
  }
}
function parseArrayOfPoints(str) {
  const arr = str.split(`
`).map((x) => x.match(/\(([^)]+)\)/)[1]);
  return arr.map(parseSinglePoint);
}
function parseArrayOfLineStrings(str) {
  const arr = str.split(`
`).map((x) => x.match(/\(([^)]+)\)/)[1]);
  return arr.map(parseLineString).reduce((acc, x) => [...acc, ...x], []);
}
function parseWKT(str) {
  if (str.startsWith("POINT")) {
    const pointStr = str.replace(/^POINT \(/, "").replace(/\)$/, "");
    return parseSinglePoint(pointStr);
  } else if (str.startsWith("MULTIPOINT")) {
    const multiPointStr = str.replace(/^MULTIPOINT \(/, "").replace(/\)$/, "");
    return parseMultiPoint(multiPointStr);
  } else if (str.startsWith("LINESTRING")) {
    const lineStr = str.replace(/^LINESTRING \(/, "").replace(/\)$/, "");
    return parseLineString(lineStr);
  } else if (str.startsWith("MULTILINESTRING")) {
    const multilineStr = str.replace(/^MULTILINESTRING /, "");
    return parseMultiLineString(multilineStr);
  } else if (str.startsWith("POLYGON") || str.startsWith("MULTIPOLYGON")) {
    return parsePolygon(str);
  } else if (str.startsWith("GEOMETRYCOLLECTION")) {
    const regex = /(?<type>POINT|LINESTRING|POLYGON|MULTIPOINT|MULTILINESTRING|MULTIPOLYGON) \((?:[^\(\)]|\([^\)]*\))*\)/g;
    const wktArray = str.match(regex);
    if (wktArray[0].startsWith("GEOMETRYCOLLECTION")) {
      wktArray[0] = wktArray[0].replace("GEOMETRYCOLLECTION (", "");
    }
    const flArray = wktArray.map(parseWKT).map((x) => x instanceof Array ? x : [x]);
    return flArray.reduce((acc, x) => [...acc, ...x], []);
  } else if (isArrayOfPoints(str)) {
    return parseArrayOfPoints(str);
  } else if (isArrayOfLines(str)) {
    return parseArrayOfLineStrings(str);
  }
  return [];
}
function isArrayOfPoints(str) {
  return str.split(`
`)?.every((str) => str.includes("POINT"));
}
function isArrayOfLines(str) {
  return str.split(`
`)?.every((str) => str.includes("LINESTRING"));
}
function isWktString(str) {
  return str.startsWith("POINT") || isArrayOfPoints(str) || str.startsWith("LINESTRING") || isArrayOfLines(str) || str.startsWith("MULTILINESTRING") || str.startsWith("POLYGON") || str.startsWith("MULTIPOINT") || str.startsWith("MULTIPOLYGON") || str.startsWith("GEOMETRYCOLLECTION");
}
Flatten.isWktString = isWktString;
Flatten.parseWKT = parseWKT;
Flatten.BooleanOperations = BooleanOperations;
Flatten.Relations = Relations;

// ../../../../tools/circuit-to-wokwi/node_modules/@tscircuit/circuit-json-util/dist/index.js
var import_transformation_matrix6 = __toESM(require_build_commonjs(), 1);
function connect(map, a, b) {
  if (!a || !b)
    return;
  let setA = map.get(a);
  if (!setA) {
    setA = /* @__PURE__ */ new Set;
    map.set(a, setA);
  }
  setA.add(b);
  let setB = map.get(b);
  if (!setB) {
    setB = /* @__PURE__ */ new Set;
    map.set(b, setB);
  }
  setB.add(a);
}
function buildSubtree(soup, opts) {
  if (!opts.subcircuit_id && !opts.source_group_id)
    return [...soup];
  let effectiveOpts = opts;
  if (opts.subcircuit_id) {
    const subcircuitIds = /* @__PURE__ */ new Set([opts.subcircuit_id]);
    const groupChildren = /* @__PURE__ */ new Map;
    const groupSubcircuit = /* @__PURE__ */ new Map;
    for (const elm of soup) {
      if (elm.type === "source_group") {
        const groupId = elm.source_group_id;
        const subcircuitId = elm.subcircuit_id;
        if (subcircuitId) {
          groupSubcircuit.set(groupId, subcircuitId);
        }
        const parentId = elm.parent_source_group_id;
        if (parentId) {
          if (!groupChildren.has(parentId)) {
            groupChildren.set(parentId, []);
          }
          groupChildren.get(parentId).push(groupId);
        }
      }
    }
    let rootGroupId;
    for (const [groupId, subcircuitId] of groupSubcircuit) {
      if (subcircuitId === opts.subcircuit_id) {
        rootGroupId = groupId;
        break;
      }
    }
    if (rootGroupId) {
      const collectChildSubcircuits = (groupId) => {
        const children = groupChildren.get(groupId) || [];
        for (const childId of children) {
          const childSubcircuit = groupSubcircuit.get(childId);
          if (childSubcircuit) {
            subcircuitIds.add(childSubcircuit);
          }
          collectChildSubcircuits(childId);
        }
      };
      collectChildSubcircuits(rootGroupId);
      effectiveOpts = { ...opts, subcircuit_ids: Array.from(subcircuitIds) };
    }
  }
  const idMap = /* @__PURE__ */ new Map;
  for (const elm of soup) {
    const idKey = `${elm.type}_id`;
    const idVal = elm[idKey];
    if (typeof idVal === "string") {
      idMap.set(idVal, elm);
    }
  }
  const adj = /* @__PURE__ */ new Map;
  for (const elm of soup) {
    const entries = Object.entries(elm);
    for (const [key, val] of entries) {
      if (key === "parent_source_group_id")
        continue;
      if (key.endsWith("_id") && typeof val === "string") {
        const other = idMap.get(val);
        connect(adj, elm, other);
      } else if (key.endsWith("_ids") && Array.isArray(val)) {
        for (const v of val) {
          if (typeof v === "string") {
            const other = idMap.get(v);
            connect(adj, elm, other);
          }
        }
      }
    }
  }
  const queue = [];
  const included = /* @__PURE__ */ new Set;
  for (const elm of soup) {
    let shouldInclude = false;
    if (effectiveOpts.subcircuit_id && "subcircuit_id" in elm && elm.subcircuit_id === effectiveOpts.subcircuit_id) {
      shouldInclude = true;
    } else if (effectiveOpts.subcircuit_ids && "subcircuit_id" in elm && elm.subcircuit_id && effectiveOpts.subcircuit_ids.includes(elm.subcircuit_id)) {
      shouldInclude = true;
    } else if (effectiveOpts.source_group_id && "source_group_id" in elm && elm.source_group_id === effectiveOpts.source_group_id) {
      shouldInclude = true;
    } else if (effectiveOpts.source_group_id && "member_source_group_ids" in elm && Array.isArray(elm.member_source_group_ids) && elm.member_source_group_ids.includes(effectiveOpts.source_group_id)) {
      shouldInclude = true;
    }
    if (shouldInclude) {
      queue.push(elm);
      included.add(elm);
    }
  }
  while (queue.length > 0) {
    const elm = queue.shift();
    const neighbors = adj.get(elm);
    if (!neighbors)
      continue;
    for (const n of neighbors) {
      if (!included.has(n)) {
        included.add(n);
        queue.push(n);
      }
    }
  }
  return soup.filter((e) => included.has(e));
}
var cju = (circuitJsonInput, options = {}) => {
  const circuitJson = circuitJsonInput;
  let internalStore = circuitJson._internal_store;
  if (!internalStore) {
    internalStore = {
      counts: {},
      editCount: 0
    };
    circuitJson._internal_store = internalStore;
    for (const elm of circuitJson) {
      const type = elm.type;
      const idVal = elm[`${type}_id`];
      if (!idVal)
        continue;
      const idNum = Number.parseInt(idVal.split("_").pop());
      if (!Number.isNaN(idNum)) {
        internalStore.counts[type] = Math.max(internalStore.counts[type] ?? 0, idNum);
      }
    }
  }
  const su2 = new Proxy({}, {
    get: (proxy_target, prop) => {
      if (prop === "toArray") {
        return () => {
          circuitJson.editCount = internalStore.editCount;
          return circuitJson;
        };
      }
      if (prop === "editCount") {
        return internalStore.editCount;
      }
      if (prop === "subtree") {
        return (opts) => cju(buildSubtree(circuitJson, opts), options);
      }
      if (prop === "insert") {
        return (elm) => {
          const component_type2 = elm.type;
          if (!component_type2) {
            throw new Error("insert requires an element with a type");
          }
          internalStore.counts[component_type2] ??= -1;
          internalStore.counts[component_type2]++;
          const index = internalStore.counts[component_type2];
          const newElm = {
            ...elm,
            type: component_type2,
            [`${component_type2}_id`]: `${component_type2}_${index}`
          };
          if (options.validateInserts) {
            const parser = exports_dist[component_type2] ?? any_soup_element;
            parser.parse(newElm);
          }
          circuitJson.push(newElm);
          internalStore.editCount++;
          return newElm;
        };
      }
      if (prop === "insertAll") {
        return (elms) => {
          return elms.map((elm) => su2.insert(elm));
        };
      }
      const component_type = prop;
      return {
        get: (id) => circuitJson.find((e) => e.type === component_type && e[`${component_type}_id`] === id),
        getUsing: (using) => {
          const keys = Object.keys(using);
          if (keys.length !== 1) {
            throw new Error("getUsing requires exactly one key, e.g. { pcb_component_id }");
          }
          const join_key = keys[0];
          const join_type = join_key.replace("_id", "");
          const joiner = circuitJson.find((e) => e.type === join_type && e[join_key] === using[join_key]);
          if (!joiner)
            return null;
          return circuitJson.find((e) => e.type === component_type && e[`${component_type}_id`] === joiner[`${component_type}_id`]);
        },
        getWhere: (where) => {
          const keys = Object.keys(where);
          return circuitJson.find((e) => e.type === component_type && keys.every((key) => e[key] === where[key]));
        },
        list: (where) => {
          const keys = !where ? [] : Object.keys(where);
          return circuitJson.filter((e) => e.type === component_type && keys.every((key) => e[key] === where[key]));
        },
        insert: (elm) => {
          internalStore.counts[component_type] ??= -1;
          internalStore.counts[component_type]++;
          const index = internalStore.counts[component_type];
          const newElm = {
            type: component_type,
            [`${component_type}_id`]: `${component_type}_${index}`,
            ...elm
          };
          if (options.validateInserts) {
            const parser = exports_dist[component_type] ?? any_soup_element;
            parser.parse(newElm);
          }
          circuitJson.push(newElm);
          internalStore.editCount++;
          return newElm;
        },
        delete: (id) => {
          const elm = circuitJson.find((e) => e[`${component_type}_id`] === id);
          if (!elm)
            return;
          circuitJson.splice(circuitJson.indexOf(elm), 1);
          internalStore.editCount++;
        },
        update: (id, newProps) => {
          const elm = circuitJson.find((e) => e.type === component_type && e[`${component_type}_id`] === id);
          if (!elm)
            return null;
          Object.assign(elm, newProps);
          internalStore.editCount++;
          return elm;
        },
        select: (selector) => {
          if (component_type === "source_component") {
            return circuitJson.find((e) => e.type === "source_component" && e.name === selector.replace(/\./g, ""));
          } else if (component_type === "pcb_port" || component_type === "source_port" || component_type === "schematic_port") {
            const [component_name, port_selector] = selector.replace(/\./g, "").split(/[\s\>]+/);
            const source_component = circuitJson.find((e) => e.type === "source_component" && e.name === component_name);
            if (!source_component)
              return null;
            const source_port = circuitJson.find((e) => e.type === "source_port" && e.source_component_id === source_component.source_component_id && (e.name === port_selector || (e.port_hints ?? []).includes(port_selector)));
            if (!source_port)
              return null;
            if (component_type === "source_port")
              return source_port;
            if (component_type === "pcb_port") {
              return circuitJson.find((e) => e.type === "pcb_port" && e.source_port_id === source_port.source_port_id);
            } else if (component_type === "schematic_port") {
              return circuitJson.find((e) => e.type === "schematic_port" && e.source_port_id === source_port.source_port_id);
            }
          }
        }
      };
    }
  });
  return su2;
};
cju.unparsed = cju;
var cju_default = cju;
function createIdKey(element) {
  const type = element.type;
  return `${type}:${element[`${type}_id`]}`;
}
var cjuIndexed = (soup, options = {}) => {
  let internalStore = soup._internal_store_indexed;
  if (!internalStore) {
    internalStore = {
      counts: {},
      editCount: 0,
      indexes: {}
    };
    for (const elm of soup) {
      const type = elm.type;
      const idVal = elm[`${type}_id`];
      if (!idVal)
        continue;
      const idNum = Number.parseInt(idVal.split("_").pop() || "");
      if (!Number.isNaN(idNum)) {
        internalStore.counts[type] = Math.max(internalStore.counts[type] ?? 0, idNum);
      }
    }
    const indexConfig = options.indexConfig || {};
    const indexes = internalStore.indexes;
    if (indexConfig.byId) {
      indexes.byId = /* @__PURE__ */ new Map;
    }
    if (indexConfig.byType) {
      indexes.byType = /* @__PURE__ */ new Map;
    }
    if (indexConfig.byRelation) {
      indexes.byRelation = /* @__PURE__ */ new Map;
    }
    if (indexConfig.bySubcircuit) {
      indexes.bySubcircuit = /* @__PURE__ */ new Map;
    }
    if (indexConfig.byCustomField && indexConfig.byCustomField.length > 0) {
      indexes.byCustomField = /* @__PURE__ */ new Map;
      for (const field of indexConfig.byCustomField) {
        indexes.byCustomField.set(field, /* @__PURE__ */ new Map);
      }
    }
    for (const element of soup) {
      if (indexConfig.byId) {
        const idKey = createIdKey(element);
        indexes.byId.set(idKey, element);
      }
      if (indexConfig.byType) {
        const elementsOfType = indexes.byType.get(element.type) || [];
        elementsOfType.push(element);
        indexes.byType.set(element.type, elementsOfType);
      }
      if (indexConfig.byRelation) {
        const elementEntries = Object.entries(element);
        for (const [key, value] of elementEntries) {
          if (key.endsWith("_id") && key !== `${element.type}_id` && typeof value === "string") {
            const relationTypeMap = indexes.byRelation.get(key) || /* @__PURE__ */ new Map;
            const relatedElements = relationTypeMap.get(value) || [];
            relatedElements.push(element);
            relationTypeMap.set(value, relatedElements);
            indexes.byRelation.set(key, relationTypeMap);
          }
        }
      }
      if (indexConfig.bySubcircuit && "subcircuit_id" in element) {
        const subcircuitId = element.subcircuit_id;
        if (subcircuitId && typeof subcircuitId === "string") {
          const subcircuitElements = indexes.bySubcircuit.get(subcircuitId) || [];
          subcircuitElements.push(element);
          indexes.bySubcircuit.set(subcircuitId, subcircuitElements);
        }
      }
      if (indexConfig.byCustomField && indexes.byCustomField) {
        for (const field of indexConfig.byCustomField) {
          if (field in element) {
            const fieldValue = element[field];
            if (fieldValue !== undefined && (typeof fieldValue === "string" || typeof fieldValue === "number")) {
              const fieldValueStr = String(fieldValue);
              const fieldMap = indexes.byCustomField.get(field);
              const elementsWithFieldValue = fieldMap.get(fieldValueStr) || [];
              elementsWithFieldValue.push(element);
              fieldMap.set(fieldValueStr, elementsWithFieldValue);
            }
          }
        }
      }
    }
    soup._internal_store_indexed = internalStore;
  }
  const suIndexed = new Proxy({}, {
    get: (proxy_target, prop) => {
      if (prop === "toArray") {
        return () => {
          soup.editCount = internalStore.editCount;
          return soup;
        };
      }
      if (prop === "editCount") {
        return internalStore.editCount;
      }
      if (prop === "insert") {
        return (elm) => {
          const { type, ...props } = elm;
          if (!type)
            throw new Error("insert requires an element with a type");
          delete props[`${type}_id`];
          return suIndexed[type].insert(props);
        };
      }
      if (prop === "insertAll") {
        return (elms) => elms.map((elm) => suIndexed.insert(elm));
      }
      if (prop === "subtree") {
        return (opts) => cjuIndexed(buildSubtree(soup, opts), options);
      }
      const component_type = prop;
      return {
        get: (id) => {
          const indexConfig = options.indexConfig || {};
          if (indexConfig.byId && internalStore.indexes.byId) {
            return internalStore.indexes.byId.get(`${component_type}:${id}`) || null;
          }
          if (indexConfig.byType && internalStore.indexes.byType) {
            const elementsOfType = internalStore.indexes.byType.get(component_type) || [];
            return elementsOfType.find((e) => e[`${component_type}_id`] === id) || null;
          }
          return soup.find((e) => e.type === component_type && e[`${component_type}_id`] === id) || null;
        },
        getUsing: (using) => {
          const indexConfig = options.indexConfig || {};
          const keys = Object.keys(using);
          if (keys.length !== 1) {
            throw new Error("getUsing requires exactly one key, e.g. { pcb_component_id }");
          }
          const join_key = keys[0];
          const join_type = join_key.replace("_id", "");
          if (indexConfig.byRelation && internalStore.indexes.byRelation) {
            const relationMap = internalStore.indexes.byRelation.get(join_key);
            if (relationMap) {
              const relatedElements = relationMap.get(using[join_key]) || [];
              const joiner2 = relatedElements.find((e) => e.type === join_type);
              if (!joiner2)
                return null;
              const joinerId = joiner2[`${component_type}_id`];
              if (indexConfig.byId && internalStore.indexes.byId) {
                return internalStore.indexes.byId.get(`${component_type}:${joinerId}`) || null;
              }
              if (indexConfig.byType && internalStore.indexes.byType) {
                const elementsOfType = internalStore.indexes.byType.get(component_type) || [];
                return elementsOfType.find((e) => e[`${component_type}_id`] === joinerId) || null;
              }
              return soup.find((e) => e.type === component_type && e[`${component_type}_id`] === joinerId) || null;
            }
          }
          const joiner = soup.find((e) => e.type === join_type && e[join_key] === using[join_key]);
          if (!joiner)
            return null;
          return soup.find((e) => e.type === component_type && e[`${component_type}_id`] === joiner[`${component_type}_id`]) || null;
        },
        getWhere: (where) => {
          const indexConfig = options.indexConfig || {};
          const keys = Object.keys(where);
          if (keys.length === 1 && indexConfig.byCustomField && internalStore.indexes.byCustomField) {
            const field = keys[0];
            const fieldMap = internalStore.indexes.byCustomField.get(field);
            if (fieldMap) {
              const fieldValue = String(where[field]);
              const elementsWithFieldValue = fieldMap.get(fieldValue) || [];
              return elementsWithFieldValue.find((e) => e.type === component_type) || null;
            }
          }
          if ("subcircuit_id" in where && indexConfig.bySubcircuit && internalStore.indexes.bySubcircuit) {
            const subcircuitId = where.subcircuit_id;
            const subcircuitElements = internalStore.indexes.bySubcircuit.get(subcircuitId) || [];
            return subcircuitElements.find((e) => e.type === component_type && keys.every((key) => e[key] === where[key])) || null;
          }
          if (indexConfig.byType && internalStore.indexes.byType) {
            const elementsOfType = internalStore.indexes.byType.get(component_type) || [];
            return elementsOfType.find((e) => keys.every((key) => e[key] === where[key])) || null;
          }
          return soup.find((e) => e.type === component_type && keys.every((key) => e[key] === where[key])) || null;
        },
        list: (where) => {
          const indexConfig = options.indexConfig || {};
          const keys = !where ? [] : Object.keys(where);
          if (keys.length === 0 && indexConfig.byType && internalStore.indexes.byType) {
            return (internalStore.indexes.byType.get(component_type) || []).slice();
          }
          if (keys.length === 1 && keys[0] === "subcircuit_id" && indexConfig.bySubcircuit && internalStore.indexes.bySubcircuit) {
            const subcircuitId = where.subcircuit_id;
            const subcircuitElements = internalStore.indexes.bySubcircuit.get(subcircuitId) || [];
            return subcircuitElements.filter((e) => e.type === component_type);
          }
          let elementsToFilter;
          if (indexConfig.byType && internalStore.indexes.byType) {
            elementsToFilter = internalStore.indexes.byType.get(component_type) || [];
          } else {
            elementsToFilter = soup.filter((e) => e.type === component_type);
          }
          if (keys.length > 0) {
            return elementsToFilter.filter((e) => keys.every((key) => e[key] === where[key]));
          }
          return elementsToFilter.slice();
        },
        insert: (elm) => {
          internalStore.counts[component_type] ??= -1;
          internalStore.counts[component_type]++;
          const index = internalStore.counts[component_type];
          const newElm = {
            type: component_type,
            [`${component_type}_id`]: `${component_type}_${index}`,
            ...elm
          };
          if (options.validateInserts) {
            const parser = exports_dist[component_type] ?? any_soup_element;
            parser.parse(newElm);
          }
          soup.push(newElm);
          internalStore.editCount++;
          const indexConfig = options.indexConfig || {};
          if (indexConfig.byId && internalStore.indexes.byId) {
            const idKey = createIdKey(newElm);
            internalStore.indexes.byId.set(idKey, newElm);
          }
          if (indexConfig.byType && internalStore.indexes.byType) {
            const elementsOfType = internalStore.indexes.byType.get(component_type) || [];
            elementsOfType.push(newElm);
            internalStore.indexes.byType.set(component_type, elementsOfType);
          }
          if (indexConfig.byRelation && internalStore.indexes.byRelation) {
            const elementEntries = Object.entries(newElm);
            for (const [key, value] of elementEntries) {
              if (key.endsWith("_id") && key !== `${newElm.type}_id` && typeof value === "string") {
                const relationTypeMap = internalStore.indexes.byRelation.get(key) || /* @__PURE__ */ new Map;
                const relatedElements = relationTypeMap.get(value) || [];
                relatedElements.push(newElm);
                relationTypeMap.set(value, relatedElements);
                internalStore.indexes.byRelation.set(key, relationTypeMap);
              }
            }
          }
          if (indexConfig.bySubcircuit && internalStore.indexes.bySubcircuit && "subcircuit_id" in newElm) {
            const subcircuitId = newElm.subcircuit_id;
            if (subcircuitId && typeof subcircuitId === "string") {
              const subcircuitElements = internalStore.indexes.bySubcircuit.get(subcircuitId) || [];
              subcircuitElements.push(newElm);
              internalStore.indexes.bySubcircuit.set(subcircuitId, subcircuitElements);
            }
          }
          if (indexConfig.byCustomField && internalStore.indexes.byCustomField) {
            for (const field of indexConfig.byCustomField) {
              if (field in newElm) {
                const fieldValue = newElm[field];
                if (fieldValue !== undefined && (typeof fieldValue === "string" || typeof fieldValue === "number")) {
                  const fieldValueStr = String(fieldValue);
                  const fieldMap = internalStore.indexes.byCustomField.get(field);
                  const elementsWithFieldValue = fieldMap.get(fieldValueStr) || [];
                  elementsWithFieldValue.push(newElm);
                  fieldMap.set(fieldValueStr, elementsWithFieldValue);
                }
              }
            }
          }
          return newElm;
        },
        delete: (id) => {
          const indexConfig = options.indexConfig || {};
          let elm;
          if (indexConfig.byId && internalStore.indexes.byId) {
            elm = internalStore.indexes.byId.get(`${component_type}:${id}`);
          } else if (indexConfig.byType && internalStore.indexes.byType) {
            const elementsOfType = internalStore.indexes.byType.get(component_type) || [];
            elm = elementsOfType.find((e) => e[`${component_type}_id`] === id);
          } else {
            elm = soup.find((e) => e[`${component_type}_id`] === id);
          }
          if (!elm)
            return;
          const elmIndex = soup.indexOf(elm);
          if (elmIndex >= 0) {
            soup.splice(elmIndex, 1);
            internalStore.editCount++;
          }
          if (indexConfig.byId && internalStore.indexes.byId) {
            const idKey = createIdKey(elm);
            internalStore.indexes.byId.delete(idKey);
          }
          if (indexConfig.byType && internalStore.indexes.byType) {
            const elementsOfType = internalStore.indexes.byType.get(component_type) || [];
            const filteredElements = elementsOfType.filter((e) => e[`${component_type}_id`] !== id);
            internalStore.indexes.byType.set(component_type, filteredElements);
          }
          if (indexConfig.byRelation && internalStore.indexes.byRelation) {
            for (const [
              relationKey,
              relationMap
            ] of internalStore.indexes.byRelation.entries()) {
              for (const [relationValue, elements] of relationMap.entries()) {
                const updatedElements = elements.filter((e) => e !== elm);
                if (updatedElements.length === 0) {
                  relationMap.delete(relationValue);
                } else {
                  relationMap.set(relationValue, updatedElements);
                }
              }
            }
          }
          if (indexConfig.bySubcircuit && internalStore.indexes.bySubcircuit && "subcircuit_id" in elm) {
            const subcircuitId = elm.subcircuit_id;
            if (subcircuitId) {
              const subcircuitElements = internalStore.indexes.bySubcircuit.get(subcircuitId) || [];
              const updatedElements = subcircuitElements.filter((e) => e !== elm);
              if (updatedElements.length === 0) {
                internalStore.indexes.bySubcircuit.delete(subcircuitId);
              } else {
                internalStore.indexes.bySubcircuit.set(subcircuitId, updatedElements);
              }
            }
          }
          if (indexConfig.byCustomField && internalStore.indexes.byCustomField) {
            for (const fieldMap of internalStore.indexes.byCustomField.values()) {
              for (const [fieldValue, elements] of fieldMap.entries()) {
                const updatedElements = elements.filter((e) => e !== elm);
                if (updatedElements.length === 0) {
                  fieldMap.delete(fieldValue);
                } else {
                  fieldMap.set(fieldValue, updatedElements);
                }
              }
            }
          }
        },
        update: (id, newProps) => {
          const indexConfig = options.indexConfig || {};
          let elm;
          if (indexConfig.byId && internalStore.indexes.byId) {
            elm = internalStore.indexes.byId.get(`${component_type}:${id}`);
          } else if (indexConfig.byType && internalStore.indexes.byType) {
            const elementsOfType = internalStore.indexes.byType.get(component_type) || [];
            elm = elementsOfType.find((e) => e[`${component_type}_id`] === id);
          } else {
            elm = soup.find((e) => e.type === component_type && e[`${component_type}_id`] === id);
          }
          if (!elm)
            return null;
          if (indexConfig.byRelation && internalStore.indexes.byRelation) {
            const elementEntries = Object.entries(elm);
            for (const [key, value] of elementEntries) {
              if (key.endsWith("_id") && key !== `${elm.type}_id` && typeof value === "string") {
                if (key in newProps && newProps[key] !== value) {
                  const relationTypeMap = internalStore.indexes.byRelation.get(key);
                  if (relationTypeMap) {
                    const relatedElements = relationTypeMap.get(value) || [];
                    const updatedElements = relatedElements.filter((e) => e !== elm);
                    if (updatedElements.length === 0) {
                      relationTypeMap.delete(value);
                    } else {
                      relationTypeMap.set(value, updatedElements);
                    }
                  }
                }
              }
            }
          }
          if (indexConfig.bySubcircuit && internalStore.indexes.bySubcircuit && "subcircuit_id" in elm && "subcircuit_id" in newProps) {
            const oldSubcircuitId = elm.subcircuit_id;
            const newSubcircuitId = newProps.subcircuit_id;
            if (oldSubcircuitId !== newSubcircuitId) {
              const subcircuitElements = internalStore.indexes.bySubcircuit.get(oldSubcircuitId) || [];
              const updatedElements = subcircuitElements.filter((e) => e !== elm);
              if (updatedElements.length === 0) {
                internalStore.indexes.bySubcircuit.delete(oldSubcircuitId);
              } else {
                internalStore.indexes.bySubcircuit.set(oldSubcircuitId, updatedElements);
              }
            }
          }
          if (indexConfig.byCustomField && internalStore.indexes.byCustomField) {
            for (const field of indexConfig.byCustomField) {
              if (field in elm && field in newProps && elm[field] !== newProps[field]) {
                const fieldMap = internalStore.indexes.byCustomField.get(field);
                if (fieldMap) {
                  const oldValue = String(elm[field]);
                  const elements = fieldMap.get(oldValue) || [];
                  const updatedElements = elements.filter((e) => e !== elm);
                  if (updatedElements.length === 0) {
                    fieldMap.delete(oldValue);
                  } else {
                    fieldMap.set(oldValue, updatedElements);
                  }
                }
              }
            }
          }
          Object.assign(elm, newProps);
          internalStore.editCount++;
          if (indexConfig.byRelation && internalStore.indexes.byRelation) {
            const elementEntries = Object.entries(elm);
            for (const [key, value] of elementEntries) {
              if (key.endsWith("_id") && key !== `${elm.type}_id` && typeof value === "string") {
                if (key in newProps) {
                  const relationTypeMap = internalStore.indexes.byRelation.get(key) || /* @__PURE__ */ new Map;
                  const relatedElements = relationTypeMap.get(value) || [];
                  if (!relatedElements.includes(elm)) {
                    relatedElements.push(elm);
                    relationTypeMap.set(value, relatedElements);
                    internalStore.indexes.byRelation.set(key, relationTypeMap);
                  }
                }
              }
            }
          }
          if (indexConfig.bySubcircuit && internalStore.indexes.bySubcircuit && "subcircuit_id" in elm && "subcircuit_id" in newProps) {
            const subcircuitId = elm.subcircuit_id;
            if (subcircuitId && typeof subcircuitId === "string") {
              const subcircuitElements = internalStore.indexes.bySubcircuit.get(subcircuitId) || [];
              if (!subcircuitElements.includes(elm)) {
                subcircuitElements.push(elm);
                internalStore.indexes.bySubcircuit.set(subcircuitId, subcircuitElements);
              }
            }
          }
          if (indexConfig.byCustomField && internalStore.indexes.byCustomField) {
            for (const field of indexConfig.byCustomField) {
              if (field in elm && field in newProps) {
                const fieldValue = elm[field];
                if (fieldValue !== undefined && (typeof fieldValue === "string" || typeof fieldValue === "number")) {
                  const fieldValueStr = String(fieldValue);
                  const fieldMap = internalStore.indexes.byCustomField.get(field);
                  const elementsWithFieldValue = fieldMap.get(fieldValueStr) || [];
                  if (!elementsWithFieldValue.includes(elm)) {
                    elementsWithFieldValue.push(elm);
                    fieldMap.set(fieldValueStr, elementsWithFieldValue);
                  }
                }
              }
            }
          }
          return elm;
        },
        select: (selector) => {
          if (component_type === "source_component") {
            return soup.find((e) => e.type === "source_component" && e.name === selector.replace(/\./g, "")) || null;
          } else if (component_type === "pcb_port" || component_type === "source_port" || component_type === "schematic_port") {
            const [component_name, port_selector] = selector.replace(/\./g, "").split(/[\s\>]+/);
            const source_component = soup.find((e) => e.type === "source_component" && e.name === component_name);
            if (!source_component)
              return null;
            const source_port = soup.find((e) => e.type === "source_port" && e.source_component_id === source_component.source_component_id && (e.name === port_selector || (e.port_hints ?? []).includes(port_selector)));
            if (!source_port)
              return null;
            if (component_type === "source_port")
              return source_port;
            if (component_type === "pcb_port") {
              return soup.find((e) => e.type === "pcb_port" && e.source_port_id === source_port.source_port_id) || null;
            } else if (component_type === "schematic_port") {
              return soup.find((e) => e.type === "schematic_port" && e.source_port_id === source_port.source_port_id) || null;
            }
          }
          return null;
        }
      };
    }
  });
  return suIndexed;
};
cjuIndexed.unparsed = cjuIndexed;
var PIN1_LOCATION_PARTS = {
  leftside_top: { side: "leftside", alignment: "top" },
  leftside_bottom: { side: "leftside", alignment: "bottom" },
  rightside_top: { side: "rightside", alignment: "top" },
  rightside_bottom: { side: "rightside", alignment: "bottom" },
  topside_left: { side: "topside", alignment: "left" },
  topside_right: { side: "topside", alignment: "right" },
  bottomside_left: { side: "bottomside", alignment: "left" },
  bottomside_right: { side: "bottomside", alignment: "right" }
};
var PIN1_LOCATIONS = Object.keys(PIN1_LOCATION_PARTS);

// ../../../../tools/circuit-to-wokwi/node_modules/circuit-json-to-connectivity-map/dist/index.js
function findConnectedNetworks(connections) {
  const networks = /* @__PURE__ */ new Map;
  let netCounter = 0;
  function getOrCreateNetwork(nodeId) {
    for (const [, network] of networks) {
      if (network.has(nodeId)) {
        return network;
      }
    }
    const newNetwork = /* @__PURE__ */ new Set;
    networks.set(`connectivity_net${netCounter++}`, newNetwork);
    return newNetwork;
  }
  for (const connection of connections) {
    let network = null;
    for (const nodeId of connection) {
      if (!network) {
        network = getOrCreateNetwork(nodeId);
      } else if (!network.has(nodeId)) {
        const existingNetwork = getOrCreateNetwork(nodeId);
        if (existingNetwork !== network) {
          for (const node of existingNetwork) {
            network.add(node);
          }
          networks.delete(Array.from(networks.entries()).find(([, net]) => net === existingNetwork)[0]);
        }
      }
      network.add(nodeId);
    }
  }
  return Object.fromEntries(Array.from(networks.entries()).map(([netId, connectedNodes]) => [
    netId,
    Array.from(connectedNodes)
  ]));
}
var ConnectivityMap = class {
  netMap;
  idToNetMap;
  constructor(netMap) {
    this.netMap = netMap;
    this.idToNetMap = {};
    for (const [netId, ids] of Object.entries(netMap)) {
      for (const id of ids) {
        this.idToNetMap[id] = netId;
      }
    }
  }
  addConnections(connections) {
    for (const connection of connections) {
      const existingNets = /* @__PURE__ */ new Set;
      for (const id of connection) {
        const existingNetId = this.idToNetMap[id];
        if (existingNetId) {
          existingNets.add(existingNetId);
        }
      }
      let targetNetId;
      if (existingNets.size === 0) {
        targetNetId = `connectivity_net${Object.keys(this.netMap).length}`;
        this.netMap[targetNetId] = [];
      } else if (existingNets.size === 1) {
        targetNetId = existingNets.values().next().value ?? `connectivity_net${Object.keys(this.netMap).length}`;
      } else {
        targetNetId = existingNets.values().next().value ?? `connectivity_net${Object.keys(this.netMap).length}`;
        for (const netId of existingNets) {
          if (netId !== targetNetId) {
            this.netMap[targetNetId].push(...this.netMap[netId]);
            this.netMap[netId] = this.netMap[targetNetId];
            for (const id of this.netMap[targetNetId]) {
              this.idToNetMap[id] = targetNetId;
            }
          }
        }
      }
      for (const id of connection) {
        if (!this.netMap[targetNetId].includes(id)) {
          this.netMap[targetNetId].push(id);
        }
        this.idToNetMap[id] = targetNetId;
      }
    }
  }
  getIdsConnectedToNet(netId) {
    return this.netMap[netId] || [];
  }
  getNetConnectedToId(id) {
    return this.idToNetMap[id];
  }
  areIdsConnected(id1, id2) {
    if (id1 === id2)
      return true;
    const netId1 = this.getNetConnectedToId(id1);
    if (!netId1)
      return false;
    const netId2 = this.getNetConnectedToId(id2);
    if (!netId2)
      return false;
    return netId1 === netId2 || netId2 === id1 || netId2 === id1;
  }
  areAllIdsConnected(ids) {
    const netId = this.getNetConnectedToId(ids[0]);
    for (const id of ids) {
      const nextNetId = this.getNetConnectedToId(id);
      if (nextNetId === undefined) {
        return false;
      }
      if (nextNetId !== netId) {
        return false;
      }
    }
    return true;
  }
};
var getSourcePortConnectivityMapFromCircuitJson = (circuitJson) => {
  const connections = [];
  for (const element of circuitJson) {
    if (element.type === "source_trace") {
      connections.push([
        ...element.connected_source_port_ids ?? [],
        ...element.connected_source_net_ids ?? []
      ]);
    } else if (element.type === "source_component") {
      if (element.internally_connected_source_port_ids) {
        for (const portGroup of element.internally_connected_source_port_ids) {
          connections.push(portGroup);
        }
      }
    } else if (element.type === "source_component_internal_connection") {
      connections.push(element.source_port_ids);
    }
  }
  const netMap = findConnectedNetworks(connections);
  return new ConnectivityMap(netMap);
};

// lib/netlist.ts
function buildNetlist(circuitJson) {
  const problems = [];
  const db = cju_default(circuitJson);
  const components = readComponents(db, problems);
  const portOwner = indexPortsByComponent(components);
  const nets = readNets(circuitJson, portOwner, db, problems);
  carryOverDesignWarnings(circuitJson, problems);
  return { netlist: { components, nets }, problems };
}
function readComponents(db, problems) {
  return db.source_component.list().map((sourceComponent) => {
    const pins = db.source_port.list({ source_component_id: sourceComponent.source_component_id }).map((port) => ({
      name: pinNameOf(port),
      portId: port.source_port_id
    }));
    if (pins.length === 0) {
      problems.push({
        message: "component has no pins in the design, so nothing can be wired to it",
        context: { component: sourceComponent.name }
      });
    }
    return {
      id: sourceComponent.source_component_id,
      name: sourceComponent.name,
      type: sourceComponent.ftype ?? "unknown",
      pins
    };
  });
}
function pinNameOf(port) {
  const hints = port.port_hints ?? [];
  const named = hints.filter((hint) => !/^(pin)?\d+$/.test(hint));
  return named[0] ?? port.name ?? hints[0] ?? port.source_port_id;
}
function indexPortsByComponent(components) {
  const owner = new Map;
  for (const component of components) {
    for (const pin of component.pins) {
      owner.set(pin.portId, { componentId: component.id, pinName: pin.name });
    }
  }
  return owner;
}
function readNets(circuitJson, portOwner, db, problems) {
  const connectivity = getSourcePortConnectivityMapFromCircuitJson(circuitJson);
  const nets = [];
  for (const [netId, portIds] of Object.entries(connectivity.netMap ?? {})) {
    const members = portIds.map((portId) => portOwner.get(portId)).filter(Boolean);
    if (members.length < 2) {
      continue;
    }
    nets.push({ id: netId, name: netNameOf(netId, portIds, db), members });
  }
  return nets.sort((a, b) => a.id.localeCompare(b.id));
}
function netNameOf(netId, portIds, db) {
  for (const net of db.source_net.list()) {
    const trace = db.source_trace.list().find((candidate) => candidate.connected_source_net_ids?.includes(net.source_net_id) && candidate.connected_source_port_ids?.some((portId) => portIds.includes(portId)));
    if (trace)
      return net.name;
  }
  return;
}
function carryOverDesignWarnings(circuitJson, problems) {
  const warnings = circuitJson.filter((element) => String(element.type).endsWith("_warning"));
  const counts = new Map;
  for (const warning of warnings) {
    counts.set(warning.type, (counts.get(warning.type) ?? 0) + 1);
  }
  for (const [type, count] of counts) {
    problems.push({ message: `the board design reports ${count} x ${type}` });
  }
}

// lib/types.ts
class ConversionFailed extends Error {
  problems;
  constructor(problems) {
    super(`${problems.length} problem(s) converting the board:
` + problems.map((problem) => `  - ${describe(problem)}`).join(`
`));
    this.problems = problems;
    this.name = "ConversionFailed";
  }
}
function describe(problem) {
  const context = problem.context ?? {};
  const parts = [
    context.component && `component ${context.component}`,
    context.pin && `pin ${context.pin}`,
    context.net && `net ${context.net}`
  ].filter(Boolean);
  return parts.length ? `${problem.message} (${parts.join(", ")})` : problem.message;
}

// lib/validate.ts
function validate(emitted, componentCount) {
  const lintProblems = lint(emitted);
  const coverageProblems = [
    ...checkNetCoverage(emitted),
    ...checkNothingVanished(emitted, componentCount)
  ];
  return {
    problems: [...lintProblems, ...coverageProblems],
    checkedNets: emitted.netOutcomes.length,
    wiredNets: emitted.netOutcomes.filter((outcome) => outcome.wires > 0).length,
    lintIssues: lintProblems.length
  };
}
function lint(emitted) {
  const result = new DiagramLinter().lint(emitted.diagram);
  return result.issues.filter((issue) => issue.severity !== "info").map((issue) => ({
    message: `${issue.rule}: ${issue.message}`,
    context: { component: issue.partId }
  }));
}
function checkNothingVanished(emitted, componentCount) {
  if (componentCount === undefined)
    return [];
  const accountedFor = emitted.diagram.parts.length + emitted.skipped.length + emitted.problems.length;
  if (accountedFor >= componentCount)
    return [];
  return [
    {
      message: `${componentCount - accountedFor} component(s) in the design became neither a part nor ` + `a stated omission. Something is being dropped silently`
    }
  ];
}
function checkNetCoverage(emitted) {
  return emitted.netOutcomes.filter((outcome) => outcome.simulatedEndpoints >= 2 && outcome.wires === 0).map((outcome) => ({
    message: "this net connects two simulated parts but produced no wire",
    context: { net: outcome.name ?? outcome.netId }
  }));
}

// cli.ts
function parseArguments(argv) {
  const options = { check: false };
  for (let index = 0;index < argv.length; index++) {
    const argument = argv[index];
    if (argument === "--check")
      options.check = true;
    else if (argument === "--circuit")
      options.circuit = argv[++index] ?? options.circuit;
    else if (argument === "--out")
      options.out = argv[++index] ?? options.out;
    else if (argument === "--mapping")
      options.mapping = argv[++index];
    else if (argument === "--chips")
      options.chips = argv[++index] ?? options.chips;
    else if (argument === "--help") {
      console.log(__doc__());
      process.exit(0);
    }
  }
  const missing = ["circuit", "out", "chips"].filter((name) => !options[name]);
  if (missing.length) {
    throw new ConversionFailed([
      {
        message: `--${missing.join(", --")} ${missing.length === 1 ? "is" : "are"} required. ` + "This tool has no default paths: it is given a design to convert, and a default " + "would be one project's layout imposed on every other."
      }
    ]);
  }
  return options;
}
function __doc__() {
  return `Usage: bun run cli.ts --circuit <circuit.json> --out <diagram.json> --chips <dir> [--mapping <wokwi-mapping.json>] [--check]

All three paths are required, and SPARK_BOARD_JSON must name the design's board file.`;
}
async function main() {
  const options = parseArguments(process.argv.slice(2));
  const circuitJson = JSON.parse(await readFile(options.circuit, "utf8"));
  if (options.mapping) {
    const spokenFor = loadMappingFile(options.mapping);
    console.log(`mapping from the part records: ${spokenFor} component(s)`);
  }
  const { netlist, problems: designProblems } = buildNetlist(circuitJson);
  const emitted = emitWokwiDiagram(netlist, { chipsDirectory: options.chips });
  const existing = await readExisting(options.out);
  const { diagram, summary } = mergeWithExisting(emitted.diagram, existing);
  const validation = validate({ ...emitted, diagram }, netlist.components.length);
  report({ netlist, emitted, summary, validation, designProblems });
  const blocking = [...emitted.problems, ...validation.problems];
  if (blocking.length)
    throw new ConversionFailed(blocking);
  const serialised = JSON.stringify(diagram, null, 2) + `
`;
  if (options.check) {
    const committed = await readFile(options.out, "utf8").catch(() => "") || "";
    if (committed !== serialised) {
      console.error(`
${options.out} is out of date.
` + `The board design has changed since the diagram was generated. Run:
` + `  bun run tools/circuit-to-wokwi/cli.ts
`);
      process.exit(1);
    }
    console.log(`
up to date: the simulation matches the board`);
    return;
  }
  await writeFile(options.out, serialised);
  console.log(`
wrote ${options.out}`);
}
async function readExisting(path) {
  try {
    return JSON.parse(await readFile(path, "utf8"));
  } catch {
    return;
  }
}
function report({ netlist, emitted, summary, validation, designProblems }) {
  console.log(`board: ${netlist.components.length} components, ${netlist.nets.length} nets
` + `diagram: ${emitted.diagram.parts.length} parts, ` + `${emitted.diagram.connections.length} wires, ` + `${validation.wiredNets}/${validation.checkedNets} nets wired`);
  if (emitted.skipped.length) {
    console.log(`
not simulated, on purpose:`);
    for (const { component, reason } of emitted.skipped) {
      console.log(`  ${component}: ${reason}`);
    }
  }
  if (summary.keptPositions || summary.keptHandAddedParts.length || summary.keptRoutes) {
    console.log(`
kept from the existing diagram: ${summary.keptPositions} positions, ` + `${summary.keptRoutes} wire routes` + (summary.keptHandAddedParts.length ? `, hand-added parts: ${summary.keptHandAddedParts.join(", ")}` : ""));
  }
  if (designProblems.length) {
    console.log(`
the board design itself reports:`);
    for (const problem of designProblems)
      console.log(`  ${problem.message}`);
  }
}
main().catch((error) => {
  console.error(`
${error.message}`);
  process.exit(1);
});
