declare module 'react-plotly.js' {
  import * as Plotly from 'plotly.js'
  import { Component } from 'react'

  export interface PlotParams {
    data: Plotly.Data[]
    layout?: Partial<Plotly.Layout>
    frames?: Plotly.Frame[]
    config?: Partial<Plotly.Config>
    /**
     * When provided, causes the plot to update only when the revision is incremented.
     */
    revision?: number
    onInitialized?: (figure: Readonly<Plotly.Figure>, graphDiv: Readonly<HTMLElement>) => void
    onUpdate?: (figure: Readonly<Plotly.Figure>, graphDiv: Readonly<HTMLElement>) => void
    onPurge?: (figure: Readonly<Plotly.Figure>, graphDiv: Readonly<HTMLElement>) => void
    onError?: (err: Error) => void
    /**
     * Callback executed after plot is interactive.
     */
    onAfterExport?: () => void
    /**
     * Callback after the user adds a new trace to the plot.
     */
    onAfterPlot?: () => void
    /**
     * Callback after the user animates the plot.
     */
    onAnimated?: () => void
    /**
     * Callback when an animation is interrupted.
     */
    onAnimatingFrame?: (event: Readonly<Plotly.FrameAnimationEvent>) => void
    /**
     * Callback when a plot is animated.
     */
    onAnimationInterrupted?: () => void
    /**
     * Callback when a plot is autosized.
     */
    onAutoSize?: () => void
    /**
     * Callback when a plot is deselected.
     */
    onBeforeExport?: () => void
    /**
     * Callback after plot is displayed.
     */
    onButtonClicked?: (event: Readonly<Plotly.ButtonClickEvent>) => void
    /**
     * Callback when the user clicks on a plot element.
     */
    onClick?: (event: Readonly<Plotly.PlotMouseEvent>) => void
    /**
     * Callback when the user clicks on a legend.
     */
    onLegendClick?: (event: Readonly<Plotly.LegendClickEvent>) => boolean | undefined
    /**
     * Callback when the user double-clicks on a legend.
     */
    onLegendDoubleClick?: (event: Readonly<Plotly.LegendDoubleClickEvent>) => boolean | undefined
    /**
     * Callback when the user drag-zooms on a plot.
     */
    onSelected?: (event: Readonly<Plotly.PlotSelectionEvent>) => void
    /**
     * Callback when the user selects an area.
     */
    onSelecting?: (event: Readonly<Plotly.PlotSelectionEvent>) => void
    /**
     * Callback when the user hover over plot.
     */
    onHover?: (event: Readonly<Plotly.PlotMouseEvent>) => void
    /**
     * Callback when the user unhover over plot.
     */
    onUnhover?: (event: Readonly<Plotly.PlotMouseEvent>) => void
    /**
     * Callback when the layout is edited.
     */
    onRelayout?: (event: Readonly<Plotly.PlotRelayoutEvent>) => void
    /**
     * Callback when the relayout is done.
     */
    onRelayouting?: (event: Readonly<Plotly.PlotRelayoutEvent>) => void
    /**
     * Callback when the user restyles the plot.
     */
    onRestyle?: (event: Readonly<Plotly.PlotRestyleEvent>) => void
    /**
     * Callback when the user redraws the plot.
     */
    onRedraw?: () => void
    /**
     * Callback when the hovering graph is cleared.
     */
    onDeselect?: () => void
    /**
     * Callback when the user double-clicks on the plot.
     */
    onDoubleClick?: () => void
    /**
     * Id of the graph div.
     */
    divId?: string
    className?: string
    style?: React.CSSProperties
    debug?: boolean
    useResizeHandler?: boolean
  }

  export default class Plot extends Component<PlotParams> {
    static prototype: Plot
  }
}
