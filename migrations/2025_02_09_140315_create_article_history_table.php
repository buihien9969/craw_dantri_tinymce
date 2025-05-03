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
        Schema::create('article_history', function (Blueprint $table) {
            $table->id('history_id');
            $table->foreignId('article_id')->constrained('articles', 'article_id');
            $table->text('content');
            $table->foreignId('edited_by')->constrained('users', 'user_id');
            $table->timestamp('edited_at')->useCurrent();
        });

    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('article_history');
    }
};
