

def test_parser():
    """
        html
            head
                script(language='text/javascript')
            body.content#body
                h1 Title
                p First paragraph.
                p Second paragraph.
                -name = 'Alpha'
                -for i in range(10):
                    i 'item {}'.format(i)
                div1.classy
                    div11
                        p
                div2
                    p
                h6 'Footer declaration.'
    """
    from .pypug import PugParser, HtmlGenerator
    from zerotk.text import dedent

    parser = PugParser()
    token_tree = parser.tokenize(dedent(test_parser.__doc__))
    generator = HtmlGenerator()
    assert generator.generate(token_tree) == dedent(
        '''
            <html>
                <head>
                    <script language='text/javascript' />
                </head>
                <body class="content" id="body">
                    <h1>Title</h1>
                    <p>First paragraph.</p>
                    <p>Second paragraph.</p>
            (CODE)<LineToken:CODE name = 'Alpha'>
            (CODE)<LineToken:CODE for i in range(10):>
                        <i>'item {}'.format(i)</i>
                    <div1 class="classy">
                        <div11>
                            <p />
                        </div11>
                    </div1>
                    <div2>
                        <p />
                    </div2>
                    <h6>'Footer declaration.'</h6>
                </body>
            </html>
        '''
    )
