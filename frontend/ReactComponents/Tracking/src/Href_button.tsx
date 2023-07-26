import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"

interface State {
  isFocused: boolean
}

/**
 * This is a React-based component template. The `render()` function is called
 * automatically when your component should be re-rendered.
 */
class Href_button extends StreamlitComponentBase<State> {
  public state = { isFocused: false }

  public render = (): ReactNode => {
    // Arguments that are passed to the plugin in Python are accessible
    // via `this.props.args`. Here, we access the "name" arg.
    const links = this.props.args["links"]

    var document_links = links.map(function (link_: string[]) {

      return <p> <a href={link_[2]}
        target="_blank"
        rel="noreferrer"
        onClick={() => Streamlit.setComponentValue(link_[0])} > {link_[1]}</a> </p>
    }
    )
    return <> {document_links}  </>

  }

}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
export default withStreamlitConnection(Href_button)
