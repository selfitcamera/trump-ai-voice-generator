import gradio as gr
import time
import uuid
from util import (
    create_task_v3, 
    get_task_result,
)


IP_Dict = {}

def generate_trump_voice_with_realtime_updates(text, word_num, request: gr.Request):
    """
    Trump AI voice generation function with real-time status updates
    """
    client_ip = request.client.host
    x_forwarded_for = dict(request.headers).get('x-forwarded-for')
    if x_forwarded_for:
        client_ip = x_forwarded_for   
    if client_ip not in IP_Dict:
        IP_Dict[client_ip] = 0
    IP_Dict[client_ip] += 1
    print(f"client_ip: {client_ip}, count: {IP_Dict[client_ip]}")
    if IP_Dict[client_ip] >= 6:
        msg = "You have reached the maximum number of requests"
        # Create "Get More Tries" button HTML
        get_more_tries_html = f"""
        <div style='display: flex; justify-content: center; gap: 30px; margin: 10px 0 25px 0; padding: 0px;'>
            <a href='https://trumpaivoice.net/#generator' target='_blank' style='
                display: inline-flex; 
                align-items: center;
                justify-content: center;
                padding: 16px 32px; 
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                color: white; 
                text-decoration: none; 
                border-radius: 12px; 
                font-weight: 600;
                font-size: 16px;
                text-align: center;
                min-width: 160px;
                box-shadow: 0 4px 15px rgba(17, 153, 142, 0.4);
                transition: all 0.3s ease;
                border: none;
            '>🚀 Get More Tries for Free</a>
        </div>
        """
        yield msg, None, "", gr.update(value=get_more_tries_html, visible=True), ""
        return msg, None, "", gr.update(value=get_more_tries_html, visible=True), ""

    if not text or len(text.strip()) < 3:
        return "Text too short, please enter at least 3 characters", None, "No task information", gr.update(visible=False), ""
    
    try:
        task_type = "voice"
        
        # Create task
        task_result = create_task_v3(task_type, text.strip(), word_num, is_rewrite=False)
        if not task_result:
            return "Failed to create task", None, "Task creation failed", gr.update(visible=False), ""
        else:
            yield "Task created successfully", None, "Task creation successful", gr.update(visible=False), ""

        max_polls = 300
        poll_interval = 1
        task_url = f"https://trumpaivoice.net/task/{task_result['uuid']}"
        
        for i in range(max_polls):
            time.sleep(poll_interval)
            task = get_task_result(task_result['uuid'])
            # print(task, i, "get_task_result")
            if task.get('data', {}):
                status = task.get('data').get('status', '')
                text_final = task.get('data').get('text_final', '')
                if status in ['completed',]:
                    voice_url = task.get('data').get('voice_url', '')
                    print(voice_url, "===>voice_url")
                    
                    # 下载音频文件到本地以避免SSRF保护问题
                    local_audio_path = voice_url
                    
                    # Create action buttons HTML
                    action_buttons_html = f"""
                    <div style='display: flex; justify-content: center; gap: 30px; margin: 25px 0; padding: 20px;'>
                        <a href='https://trumpaivoice.net/#generator' target='_blank' style='
                            display: inline-flex; 
                            align-items: center;
                            justify-content: center;
                            padding: 16px 32px; 
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white; 
                            text-decoration: none; 
                            border-radius: 12px; 
                            font-weight: 600;
                            font-size: 16px;
                            text-align: center;
                            min-width: 160px;
                            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                            transition: all 0.3s ease;
                            border: none;
                        '>🎬 Generate Video</a>
                        <a href='{task_url}' target='_blank' style='
                            display: inline-flex; 
                            align-items: center;
                            justify-content: center;
                            padding: 16px 32px; 
                            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                            color: white; 
                            text-decoration: none; 
                            border-radius: 12px; 
                            font-weight: 600;
                            font-size: 16px;
                            text-align: center;
                            min-width: 160px;
                            box-shadow: 0 4px 15px rgba(17, 153, 142, 0.4);
                            transition: all 0.3s ease;
                            border: none;
                        '>👀 Check Generate Details</a>
                    </div>
                    """
                    yield f"✅ success!!!", local_audio_path, text_final, gr.update(value=action_buttons_html, visible=True), task_url
                    return "✅ Generation successful!", local_audio_path, "success", gr.update(value=action_buttons_html, visible=True), task_url
                elif status in ['failed', 'voice_error', 'no_credits']:
                    yield "❌ Generation failed!", None, None, gr.update(visible=False), ""
                    return "❌ Generation failed!", None, None, gr.update(visible=False), ""
                else:
                    yield f"query {i} times, on processing, go to task page {task_url} to check status", None, text_final, gr.update(visible=False), task_url
        return "❌ Generation failed!", None, None, gr.update(visible=False), ""
    except Exception as e:
        error_msg = f"Generation failed: {str(e)}"
        yield error_msg, None, f"❌ Error message: {error_msg}", gr.update(visible=False), ""
        return error_msg, None, f"❌ Error message: {error_msg}", gr.update(visible=False), ""

# Create Gradio Interface
with gr.Blocks(title="Donald Trump AI Voice", theme=gr.themes.Soft()) as demo:
    
    # Main title - at the top
    gr.HTML("""
    <div style="text-align: center; margin: 5px auto 0px auto; max-width: 800px;">
        <h1 style="color: #2c3e50; margin: 0; font-size: 3.5em; font-weight: 800; letter-spacing: 3px; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);">
            🎤 Trump AI Voice
        </h1>
    </div>
    """, padding=False)
    
    # # Showcase link banner - second
    # gr.HTML("""
    # <div style="text-align: center; margin: 0px auto 40px auto; max-width: 600px;">
    #     <div style="background: linear-gradient(135deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%); padding: 15px 5px; border-radius: 15px; box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);">
    #         <h3 style="color: white; margin: 0; font-size: 18px;">
    #             🎬 <a href="https://trumpaivoice.net/showcase" target="_blank" style="color: white; text-decoration: none; font-weight: bold;">Check out Trump AI videos created by others →</a>
    #         </h3>
    #     </div>
    # </div>
    # """, padding=False)

    # Powered by link - small text
    gr.HTML("""
    <div style="text-align: center; margin: 0px auto -5px auto;">
        <p style="margin: 0; font-size: 16px; color: #999; font-weight: 400;">
            powered by <a href="https://trumpaivoice.net/" target="_blank" style="color: #667eea; text-decoration: none;">trumpaivoice.net</a>
        </p>
    </div>
    """, padding=False)
    
    # Simple description text - third
    # gr.HTML("""
    # <div style="text-align: center; margin: 15px auto 30px auto; max-width: 500px;">
    #     <p style="color: #666; margin: 0; font-size: 1em; font-weight: 500; line-height: 1.4;">
    #         🔥 Try the most advanced Trump AI Voice and Video generator for FREE at 
    #         <a href="https://trumpaivoice.net/" target="_blank" style="color: #667eea; text-decoration: none; font-weight: bold;">donaldtrumpaivoice.com</a>!
    #     </p>
    # </div>
    # """)
    
    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(
                label="📝 Input Text",
                lines=4,
                placeholder="Enter what you want Trump to say...",
                value="Hello everyone, this is a demonstration of the Trump AI Voice system with real-time status monitoring."
            )
        
        with gr.Column(scale=1):
            word_num_slider = gr.Slider(
                20, 60, value=60, step=1,
                label="⏱️ Duration Limit"
            )

            submit_btn = gr.Button(
                "🚀 Generate Trump AI Voice",
                variant="primary",
                size="lg"
            )
    
    with gr.Row():
        status_output = gr.Textbox(
            label="📊 Status",
            interactive=False,
            placeholder="Waiting for generation..."
        )
    
    # Action buttons that will show after task completion
    with gr.Row():
        action_links = gr.HTML(visible=False)
    
    with gr.Row():
        audio_output = gr.Audio(
            label="🎵 Trump AI Voice",
            interactive=False
        )
    
    with gr.Row():
        task_info = gr.Textbox(
            label="📋 AI Rewritten Text with Latest News",
            interactive=False,
            lines=12,
            placeholder="AI rewritten text with the latest news will be shown here..."
        )
    

    # Comprehensive introduction section
    gr.HTML("""
    <div style="width: 100%; margin: 30px 0; padding: 0 20px;">
        
        <!-- Hero Description -->
        <div style="text-align: center; margin: 25px auto; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
            <h2 style="color: #2c3e50; margin: 0 0 15px 0; font-size: 1.8em; font-weight: 700;">
                🇺🇸 Experience the Power of AI-Generated Trump Voice
            </h2>
                         <p style="color: #555; font-size: 1.1em; line-height: 1.6; margin: 0 0 20px 0; width: 100%; padding: 0 20px;">
                 Transform any text into authentic Donald Trump speech with our cutting-edge AI voice synthesis technology. 
                 Whether you're creating content for entertainment, education, or social media, our advanced neural network 
                 captures Trump's distinctive speaking style, intonation, and rhetorical patterns with remarkable accuracy.
             </p>
             <div style="text-align: center; margin: 15px 0;">
                 <a href="https://trumpaivoice.net/" target="_blank" style="
                     display: inline-flex; 
                     align-items: center;
                     justify-content: center;
                     padding: 12px 28px; 
                     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                     color: white; 
                     text-decoration: none; 
                     border-radius: 10px; 
                     font-weight: 600;
                     font-size: 14px;
                     box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                     transition: all 0.3s ease;
                 ">🎬 Generate Trump AI Videos & More →</a>
             </div>
        </div>

        <!-- Features Grid -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin: 40px 0;">
            
            <div style="background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); border-left: 5px solid #e74c3c;">
                <h3 style="color: #e74c3c; margin: 0 0 12px 0; font-size: 1.3em; font-weight: 600;">
                    🎯 Ultra-Realistic Voice
                </h3>
                <p style="color: #666; margin: 0; line-height: 1.5; font-size: 0.95em;">
                    Our AI model is trained on thousands of hours of Trump speeches, capturing his unique vocal characteristics, 
                    pronunciation patterns, and speaking rhythm to deliver incredibly lifelike results.
                </p>
            </div>

            <div style="background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); border-left: 5px solid #3498db;">
                <h3 style="color: #3498db; margin: 0 0 12px 0; font-size: 1.3em; font-weight: 600;">
                    ⚡ Lightning Fast Generation
                </h3>
                <p style="color: #666; margin: 0; line-height: 1.5; font-size: 0.95em;">
                    Generate high-quality Trump AI voice clips in seconds, not minutes. Our optimized infrastructure 
                    ensures rapid processing while maintaining exceptional audio quality.
                </p>
            </div>

            <div style="background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); border-left: 5px solid #27ae60;">
                <h3 style="color: #27ae60; margin: 0 0 12px 0; font-size: 1.3em; font-weight: 600;">
                    🎨 Creative Content Creation
                </h3>
                <p style="color: #666; margin: 0; line-height: 1.5; font-size: 0.95em;">
                    Perfect for memes, podcasts, educational content, entertainment videos, or any creative project 
                    that needs an authentic Trump voice performance.
                </p>
            </div>

        </div>

        
                 <!-- Celebrity Voices Section -->
         <div style="background: linear-gradient(135deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%); color: white; padding: 40px; border-radius: 20px; margin: 40px 0; text-align: center;">
             <h2 style="margin: 0 0 20px 0; font-size: 1.8em; font-weight: 700;">
                 🎭 Try More Celebrity AI Voices
             </h2>
             <p style="margin: 0 0 25px 0; font-size: 1.1em; opacity: 0.95; line-height: 1.5;">
                 Explore our premium collection of celebrity AI voices! Our high-quality service delivers 
                 lightning-fast results with exceptional audio quality. Experience the best AI voice generation 
                 with our reliable and responsive platform.
             </p>
             <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
                 <a href="https://trumpaivoice.net/explore" target="_blank" style="
                     display: inline-flex; 
                     align-items: center;
                     justify-content: center;
                     padding: 18px 35px; 
                     background: rgba(255,255,255,0.9);
                     color: #333; 
                     text-decoration: none; 
                     border-radius: 15px; 
                     font-weight: 700;
                     font-size: 16px;
                     text-align: center;
                     min-width: 200px;
                     box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                     transition: all 0.3s ease;
                     border: none;
                 ">🌟 Explore Celebrity Voices</a>
                 <a href="https://trumpaivoice.net/showcase" target="_blank" style="
                     display: inline-flex; 
                     align-items: center;
                     justify-content: center;
                     padding: 18px 35px; 
                     background: rgba(255,255,255,0.2);
                     color: white; 
                     text-decoration: none; 
                     border-radius: 15px; 
                     font-weight: 700;
                     font-size: 16px;
                     text-align: center;
                     min-width: 200px;
                     box-shadow: 0 6px 20px rgba(0,0,0,0.2);
                     transition: all 0.3s ease;
                     border: 2px solid rgba(255,255,255,0.3);
                 ">🎭 View Showcase</a>
             </div>
         </div>

        <!-- Tips Section -->
        <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%); padding: 25px; border-radius: 15px; margin: 40px 0;">
            <h3 style="color: #8b5cf6; text-align: center; margin: 0 0 20px 0; font-size: 1.4em; font-weight: 700;">
                💡 Pro Tips for Best Results
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px;">
                
                <div style="background: rgba(255,255,255,0.8); padding: 15px; border-radius: 10px;">
                    <strong style="color: #8b5cf6;">📖 Clear Text:</strong>
                    <span style="color: #555;"> Use proper punctuation and avoid special characters for optimal results.</span>
                </div>

                <div style="background: rgba(255,255,255,0.8); padding: 15px; border-radius: 10px;">
                    <strong style="color: #8b5cf6;">⏱️ Length Matters:</strong>
                    <span style="color: #555;"> Shorter texts (20-60 words) typically produce the most natural-sounding results.</span>
                </div>

                <div style="background: rgba(255,255,255,0.8); padding: 15px; border-radius: 10px;">
                    <strong style="color: #8b5cf6;">🎯 Trump Style:</strong>
                    <span style="color: #555;"> Text written in Trump's speaking style will sound more authentic and natural.</span>
                </div>

            </div>
        </div>

    </div>
    """, padding=False)
    

    # Powered by link - small text
    gr.HTML("""
    <div style="text-align: center; margin: 0px auto -5px auto;">
        <p style="margin: 0; font-size: 16px; color: #999; font-weight: 400;">
            Click <a href="https://trumpaivoice.net/showcase" target="_blank" style="color: #667eea; text-decoration: none;"> trump ai voices showcase </a> to see more videos
        </p>
    </div>
    """, padding=False)

    # Hidden state to store task_url
    task_url_state = gr.State("")

    # Bind event
    submit_btn.click(
        generate_trump_voice_with_realtime_updates,
        inputs=[text_input, word_num_slider],
        outputs=[status_output, audio_output, task_info, action_links, task_url_state]
    )

if __name__ == "__main__":
    demo.launch() 