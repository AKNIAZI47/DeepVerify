/*
 * ATTENTION: An "eval-source-map" devtool has been used.
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file with attached SourceMaps in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(() => {
var exports = {};
exports.id = "pages/_app";
exports.ids = ["pages/_app"];
exports.modules = {

/***/ "./src/components/InteractiveBackground.tsx":
/*!**************************************************!*\
  !*** ./src/components/InteractiveBackground.tsx ***!
  \**************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (/* binding */ InteractiveBackground)\n/* harmony export */ });\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react/jsx-dev-runtime */ \"react/jsx-dev-runtime\");\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ \"react\");\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);\n\n\nfunction InteractiveBackground() {\n    const [mousePosition, setMousePosition] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)({\n        x: 50,\n        y: 50\n    });\n    (0,react__WEBPACK_IMPORTED_MODULE_1__.useEffect)(()=>{\n        const handleMouseMove = (e)=>{\n            // Convert mouse position to percentage of viewport\n            const x = e.clientX / window.innerWidth * 100;\n            const y = e.clientY / window.innerHeight * 100;\n            setMousePosition({\n                x,\n                y\n            });\n        };\n        window.addEventListener(\"mousemove\", handleMouseMove);\n        return ()=>{\n            window.removeEventListener(\"mousemove\", handleMouseMove);\n        };\n    }, []);\n    return /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(\"div\", {\n        style: {\n            position: \"fixed\",\n            top: 0,\n            left: 0,\n            width: \"100%\",\n            height: \"100%\",\n            zIndex: -1,\n            pointerEvents: \"none\",\n            background: `\r\n          radial-gradient(circle at ${mousePosition.x}% ${mousePosition.y}%, \r\n            rgba(92, 225, 255, 0.15) 0%, \r\n            transparent 50%),\r\n          radial-gradient(circle at ${100 - mousePosition.x}% ${100 - mousePosition.y}%, \r\n            rgba(255, 92, 225, 0.10) 0%, \r\n            transparent 50%),\r\n          radial-gradient(circle at ${mousePosition.x}% ${100 - mousePosition.y}%, \r\n            rgba(124, 139, 255, 0.12) 0%, \r\n            transparent 50%),\r\n          #000000\r\n        `,\n            transition: \"background 0.3s ease-out\"\n        }\n    }, void 0, false, {\n        fileName: \"C:\\\\Users\\\\Anas Computer\\\\Downloads\\\\Fake-News-main\\\\Fake-News-main\\\\frontend\\\\src\\\\components\\\\InteractiveBackground.tsx\",\n        lineNumber: 22,\n        columnNumber: 5\n    }, this);\n}\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY29tcG9uZW50cy9JbnRlcmFjdGl2ZUJhY2tncm91bmQudHN4IiwibWFwcGluZ3MiOiI7Ozs7Ozs7OztBQUE0QztBQUU3QixTQUFTRTtJQUN0QixNQUFNLENBQUNDLGVBQWVDLGlCQUFpQixHQUFHSiwrQ0FBUUEsQ0FBQztRQUFFSyxHQUFHO1FBQUlDLEdBQUc7SUFBRztJQUVsRUwsZ0RBQVNBLENBQUM7UUFDUixNQUFNTSxrQkFBa0IsQ0FBQ0M7WUFDdkIsbURBQW1EO1lBQ25ELE1BQU1ILElBQUksRUFBR0ksT0FBTyxHQUFHQyxPQUFPQyxVQUFVLEdBQUk7WUFDNUMsTUFBTUwsSUFBSSxFQUFHTSxPQUFPLEdBQUdGLE9BQU9HLFdBQVcsR0FBSTtZQUM3Q1QsaUJBQWlCO2dCQUFFQztnQkFBR0M7WUFBRTtRQUMxQjtRQUVBSSxPQUFPSSxnQkFBZ0IsQ0FBQyxhQUFhUDtRQUVyQyxPQUFPO1lBQ0xHLE9BQU9LLG1CQUFtQixDQUFDLGFBQWFSO1FBQzFDO0lBQ0YsR0FBRyxFQUFFO0lBRUwscUJBQ0UsOERBQUNTO1FBQ0NDLE9BQU87WUFDTEMsVUFBVTtZQUNWQyxLQUFLO1lBQ0xDLE1BQU07WUFDTkMsT0FBTztZQUNQQyxRQUFRO1lBQ1JDLFFBQVEsQ0FBQztZQUNUQyxlQUFlO1lBQ2ZDLFlBQVksQ0FBQztvQ0FDZSxFQUFFdEIsY0FBY0UsQ0FBQyxDQUFDLEVBQUUsRUFBRUYsY0FBY0csQ0FBQyxDQUFDOzs7b0NBR3RDLEVBQUUsTUFBTUgsY0FBY0UsQ0FBQyxDQUFDLEVBQUUsRUFBRSxNQUFNRixjQUFjRyxDQUFDLENBQUM7OztvQ0FHbEQsRUFBRUgsY0FBY0UsQ0FBQyxDQUFDLEVBQUUsRUFBRSxNQUFNRixjQUFjRyxDQUFDLENBQUM7Ozs7UUFJeEUsQ0FBQztZQUNEb0IsWUFBWTtRQUNkOzs7Ozs7QUFHTiIsInNvdXJjZXMiOlsid2VicGFjazovL3ZlcmlnbG93LWZyb250ZW5kLy4vc3JjL2NvbXBvbmVudHMvSW50ZXJhY3RpdmVCYWNrZ3JvdW5kLnRzeD85ZWU3Il0sInNvdXJjZXNDb250ZW50IjpbImltcG9ydCB7IHVzZVN0YXRlLCB1c2VFZmZlY3QgfSBmcm9tICdyZWFjdCc7XHJcblxyXG5leHBvcnQgZGVmYXVsdCBmdW5jdGlvbiBJbnRlcmFjdGl2ZUJhY2tncm91bmQoKSB7XHJcbiAgY29uc3QgW21vdXNlUG9zaXRpb24sIHNldE1vdXNlUG9zaXRpb25dID0gdXNlU3RhdGUoeyB4OiA1MCwgeTogNTAgfSk7XHJcblxyXG4gIHVzZUVmZmVjdCgoKSA9PiB7XHJcbiAgICBjb25zdCBoYW5kbGVNb3VzZU1vdmUgPSAoZTogTW91c2VFdmVudCkgPT4ge1xyXG4gICAgICAvLyBDb252ZXJ0IG1vdXNlIHBvc2l0aW9uIHRvIHBlcmNlbnRhZ2Ugb2Ygdmlld3BvcnRcclxuICAgICAgY29uc3QgeCA9IChlLmNsaWVudFggLyB3aW5kb3cuaW5uZXJXaWR0aCkgKiAxMDA7XHJcbiAgICAgIGNvbnN0IHkgPSAoZS5jbGllbnRZIC8gd2luZG93LmlubmVySGVpZ2h0KSAqIDEwMDtcclxuICAgICAgc2V0TW91c2VQb3NpdGlvbih7IHgsIHkgfSk7XHJcbiAgICB9O1xyXG5cclxuICAgIHdpbmRvdy5hZGRFdmVudExpc3RlbmVyKCdtb3VzZW1vdmUnLCBoYW5kbGVNb3VzZU1vdmUpO1xyXG5cclxuICAgIHJldHVybiAoKSA9PiB7XHJcbiAgICAgIHdpbmRvdy5yZW1vdmVFdmVudExpc3RlbmVyKCdtb3VzZW1vdmUnLCBoYW5kbGVNb3VzZU1vdmUpO1xyXG4gICAgfTtcclxuICB9LCBbXSk7XHJcblxyXG4gIHJldHVybiAoXHJcbiAgICA8ZGl2XHJcbiAgICAgIHN0eWxlPXt7XHJcbiAgICAgICAgcG9zaXRpb246ICdmaXhlZCcsXHJcbiAgICAgICAgdG9wOiAwLFxyXG4gICAgICAgIGxlZnQ6IDAsXHJcbiAgICAgICAgd2lkdGg6ICcxMDAlJyxcclxuICAgICAgICBoZWlnaHQ6ICcxMDAlJyxcclxuICAgICAgICB6SW5kZXg6IC0xLFxyXG4gICAgICAgIHBvaW50ZXJFdmVudHM6ICdub25lJyxcclxuICAgICAgICBiYWNrZ3JvdW5kOiBgXHJcbiAgICAgICAgICByYWRpYWwtZ3JhZGllbnQoY2lyY2xlIGF0ICR7bW91c2VQb3NpdGlvbi54fSUgJHttb3VzZVBvc2l0aW9uLnl9JSwgXHJcbiAgICAgICAgICAgIHJnYmEoOTIsIDIyNSwgMjU1LCAwLjE1KSAwJSwgXHJcbiAgICAgICAgICAgIHRyYW5zcGFyZW50IDUwJSksXHJcbiAgICAgICAgICByYWRpYWwtZ3JhZGllbnQoY2lyY2xlIGF0ICR7MTAwIC0gbW91c2VQb3NpdGlvbi54fSUgJHsxMDAgLSBtb3VzZVBvc2l0aW9uLnl9JSwgXHJcbiAgICAgICAgICAgIHJnYmEoMjU1LCA5MiwgMjI1LCAwLjEwKSAwJSwgXHJcbiAgICAgICAgICAgIHRyYW5zcGFyZW50IDUwJSksXHJcbiAgICAgICAgICByYWRpYWwtZ3JhZGllbnQoY2lyY2xlIGF0ICR7bW91c2VQb3NpdGlvbi54fSUgJHsxMDAgLSBtb3VzZVBvc2l0aW9uLnl9JSwgXHJcbiAgICAgICAgICAgIHJnYmEoMTI0LCAxMzksIDI1NSwgMC4xMikgMCUsIFxyXG4gICAgICAgICAgICB0cmFuc3BhcmVudCA1MCUpLFxyXG4gICAgICAgICAgIzAwMDAwMFxyXG4gICAgICAgIGAsXHJcbiAgICAgICAgdHJhbnNpdGlvbjogJ2JhY2tncm91bmQgMC4zcyBlYXNlLW91dCcsXHJcbiAgICAgIH19XHJcbiAgICAvPlxyXG4gICk7XHJcbn1cclxuIl0sIm5hbWVzIjpbInVzZVN0YXRlIiwidXNlRWZmZWN0IiwiSW50ZXJhY3RpdmVCYWNrZ3JvdW5kIiwibW91c2VQb3NpdGlvbiIsInNldE1vdXNlUG9zaXRpb24iLCJ4IiwieSIsImhhbmRsZU1vdXNlTW92ZSIsImUiLCJjbGllbnRYIiwid2luZG93IiwiaW5uZXJXaWR0aCIsImNsaWVudFkiLCJpbm5lckhlaWdodCIsImFkZEV2ZW50TGlzdGVuZXIiLCJyZW1vdmVFdmVudExpc3RlbmVyIiwiZGl2Iiwic3R5bGUiLCJwb3NpdGlvbiIsInRvcCIsImxlZnQiLCJ3aWR0aCIsImhlaWdodCIsInpJbmRleCIsInBvaW50ZXJFdmVudHMiLCJiYWNrZ3JvdW5kIiwidHJhbnNpdGlvbiJdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./src/components/InteractiveBackground.tsx\n");

/***/ }),

/***/ "./src/pages/_app.tsx":
/*!****************************!*\
  !*** ./src/pages/_app.tsx ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (/* binding */ App)\n/* harmony export */ });\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react/jsx-dev-runtime */ \"react/jsx-dev-runtime\");\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var _styles_globals_css__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../styles/globals.css */ \"./src/styles/globals.css\");\n/* harmony import */ var _styles_globals_css__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_styles_globals_css__WEBPACK_IMPORTED_MODULE_1__);\n/* harmony import */ var _components_InteractiveBackground__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../components/InteractiveBackground */ \"./src/components/InteractiveBackground.tsx\");\n\n\n\nfunction App({ Component, pageProps }) {\n    return /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.Fragment, {\n        children: [\n            /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(_components_InteractiveBackground__WEBPACK_IMPORTED_MODULE_2__[\"default\"], {}, void 0, false, {\n                fileName: \"C:\\\\Users\\\\Anas Computer\\\\Downloads\\\\Fake-News-main\\\\Fake-News-main\\\\frontend\\\\src\\\\pages\\\\_app.tsx\",\n                lineNumber: 8,\n                columnNumber: 7\n            }, this),\n            /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(Component, {\n                ...pageProps\n            }, void 0, false, {\n                fileName: \"C:\\\\Users\\\\Anas Computer\\\\Downloads\\\\Fake-News-main\\\\Fake-News-main\\\\frontend\\\\src\\\\pages\\\\_app.tsx\",\n                lineNumber: 9,\n                columnNumber: 7\n            }, this)\n        ]\n    }, void 0, true);\n}\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvcGFnZXMvX2FwcC50c3giLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7OztBQUErQjtBQUV5QztBQUV6RCxTQUFTQyxJQUFJLEVBQUVDLFNBQVMsRUFBRUMsU0FBUyxFQUFZO0lBQzVELHFCQUNFOzswQkFDRSw4REFBQ0gseUVBQXFCQTs7Ozs7MEJBQ3RCLDhEQUFDRTtnQkFBVyxHQUFHQyxTQUFTOzs7Ozs7OztBQUc5QiIsInNvdXJjZXMiOlsid2VicGFjazovL3ZlcmlnbG93LWZyb250ZW5kLy4vc3JjL3BhZ2VzL19hcHAudHN4P2Y5ZDYiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IFwiLi4vc3R5bGVzL2dsb2JhbHMuY3NzXCI7XG5pbXBvcnQgdHlwZSB7IEFwcFByb3BzIH0gZnJvbSBcIm5leHQvYXBwXCI7XG5pbXBvcnQgSW50ZXJhY3RpdmVCYWNrZ3JvdW5kIGZyb20gXCIuLi9jb21wb25lbnRzL0ludGVyYWN0aXZlQmFja2dyb3VuZFwiO1xuXG5leHBvcnQgZGVmYXVsdCBmdW5jdGlvbiBBcHAoeyBDb21wb25lbnQsIHBhZ2VQcm9wcyB9OiBBcHBQcm9wcykge1xuICByZXR1cm4gKFxuICAgIDw+XG4gICAgICA8SW50ZXJhY3RpdmVCYWNrZ3JvdW5kIC8+XG4gICAgICA8Q29tcG9uZW50IHsuLi5wYWdlUHJvcHN9IC8+XG4gICAgPC8+XG4gICk7XG59Il0sIm5hbWVzIjpbIkludGVyYWN0aXZlQmFja2dyb3VuZCIsIkFwcCIsIkNvbXBvbmVudCIsInBhZ2VQcm9wcyJdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./src/pages/_app.tsx\n");

/***/ }),

/***/ "./src/styles/globals.css":
/*!********************************!*\
  !*** ./src/styles/globals.css ***!
  \********************************/
/***/ (() => {



/***/ }),

/***/ "react":
/*!************************!*\
  !*** external "react" ***!
  \************************/
/***/ ((module) => {

"use strict";
module.exports = require("react");

/***/ }),

/***/ "react/jsx-dev-runtime":
/*!****************************************!*\
  !*** external "react/jsx-dev-runtime" ***!
  \****************************************/
/***/ ((module) => {

"use strict";
module.exports = require("react/jsx-dev-runtime");

/***/ })

};
;

// load runtime
var __webpack_require__ = require("../webpack-runtime.js");
__webpack_require__.C(exports);
var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
var __webpack_exports__ = (__webpack_exec__("./src/pages/_app.tsx"));
module.exports = __webpack_exports__;

})();