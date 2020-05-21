
import React, {useState} from 'react';
import DefaultPixelPreview from './tmp-pixel-lanczos.jpg';

import './PixelImagePreview.scss';


function PixelImagePreview(props) {

    let [loaded, setLoaded] = useState(false);

    const src = props.src;
    const alt = "alt" in props ? props.alt : "-";

    let previewSrc;

    if ("previewAppendix" in props) {
        previewSrc = insertAppendix(src, props["previewAppendix"]);
    } else if ("previewSrc" in props) {
        previewSrc = props["previewSrc"];
    } else {
        previewSrc = DefaultPixelPreview;
    }

    return (
        <React.Fragment>
            <img alt={alt} className="imageComponent" style={{display: loaded ? "block" : "none"}}
                 src={src} onLoad={() => setLoaded(true)}
            />
            <img alt={alt} className="imageComponent pixelImagePreview"
                 style={{display: loaded ? "none" : "block"}} src={previewSrc}
            />
        </React.Fragment>
    )
}


function insertAppendix(filename, appendix) {
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
