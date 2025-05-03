<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('article_media', function (Blueprint $table) {
            $table->id('media_id');
            $table->foreignId('article_id')->constrained('articles', 'article_id');
            $table->enum('media_type', ['image', 'video', 'link']);
            $table->string('media_url', 255);
            $table->text('caption')->nullable();
            $table->integer('position');
            $table->timestamp('created_at')->useCurrent();
        });

    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('article_media');
    }
};
