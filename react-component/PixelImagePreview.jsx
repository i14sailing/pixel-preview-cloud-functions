
import React from 'react';
import './PixelImagePreview.scss';


const MOUNTING_DELAY = 300;


class PixelImagePreview extends React.Component {

    constructor(props) {
        super(props);

        const alt = "alt" in this.props ? this.props.alt : "-";
        const src = this.props.src;
        const previewSrc = getPreviewSrc(props);

        // The state alt, previewSrc and pendingSrc switches right away!

        // After the MOUTING_DELAY the src switches as well and the <img>
        // with the full src is actually mounted in the DOM

        this.state = {
            alt: alt,
            previewSrc: previewSrc,

            mounted: false,
            loaded: false,
            src: "",
            pendindSrc: src,
            pendingUpdate: undefined,
        }

        this.state.pendingUpdate = setTimeout(() => {
            console.log("initial mounting");
            this.setState({mounted: true, src: src});
        }, MOUNTING_DELAY);
    }

    componentDidUpdate(prevProps, prevState, SS) {
        const newAlt = "alt" in this.props ? this.props.alt : "-";
        const newSrc = this.props.src;
        const newPreviewSrc = getPreviewSrc(this.props);

        if (this.state.pendingSrc !== newSrc || this.state.previewSrc !== newPreviewSrc) {
            // Every time the pendingSrc (=src after MOUNTING_DELAY) or previewSrc changes

            if (this.state.mounted || (this.state.pendingSrc !== newSrc)) {
                // this.state.mounted -> when old image was mounted

                // this.state.pendingSrc !== newSrc -> when old image was not mounted
                // (very fast src prop changes)

                if (this.state.mounted) {
                    console.log("un-mounting");
                }

                // Abort pendingUpdate
                clearTimeout(this.state.pendingUpdate);

                // Initialize new pendingUpdate
                let pendingUpdate = setTimeout(() => {
                    console.log("re-mounting");
                    this.setState({alt: newAlt, src: newSrc, mounted: true});
                }, MOUNTING_DELAY);

                // Update state to new PixelPreview
                this.setState({mounted: false, loaded: false, previewSrc: newPreviewSrc,
                    pendingUpdate: pendingUpdate, pendingSrc: newSrc})
            }
        }
    }

    render() {

        return (
            <React.Fragment>
                {this.state.mounted && (
                    <img alt={this.state.alt} className="imageComponent" style={{display: (this.state.loaded ? "block" : "none")}}
                         src={this.state.src} onLoad={() => this.setState({loaded: true})}
                    />
                )}
                <img alt={this.state.alt} className="imageComponent pixelImagePreview"
                     style={{display: (this.state.loaded ? "none" : "block")}} src={this.state.previewSrc}
                />
            </React.Fragment>
        )
    }
}


function getPreviewSrc(props) {
    let previewSrc = "";

    if ("previewAppendix" in props) {
        previewSrc = insertAppendix(props.src, props["previewAppendix"]);
    } else if ("previewSrc" in props) {
        previewSrc = props["previewSrc"];
    }

    return previewSrc;
}

export function insertAppendix(filename, appendix) {
    let filenameList = filename.split(".");
    let newFilename = ""
    for (let i=0; i<filenameList.length - 1; i++) {
        newFilename += filenameList[i]
        if (i !== filenameList.length - 2) {
            newFilename += "."
        }
    }
    return newFilename + appendix + "." + filenameList[filenameList.length - 1];
}


export default PixelImagePreview;
